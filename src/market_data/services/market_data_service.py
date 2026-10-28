from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np

from src.core.exceptions import MarketDataUnavailableError, TickerNotFoundError

from src.market_data.calibrators.implied_spot import ImpliedSpotFromParity
from src.market_data.calibrators.implied_volatility import ImpliedVolatilityBS
from src.market_data.calibrators.term_structure_builder import TermStructureBuilder
from src.market_data.calibrators.volatility_smile_builder import VolatilitySmileBuilder
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.volatility_smile_curve import VolatilitySmileCurve
from src.market_data.curves.volatility_term_structure_curve import VolatilityTermStructureCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.loaders.dividend_loader import build_dividend_yield
from src.market_data.loaders.rates_loader import build_rate_curve
from src.market_data.loaders.spot_loader import load_spot
from src.market_data.loaders.volatilityLoader import filter_quotes, get_all_option_quotes
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.models.iv_quote import IVQuote
from src.market_data.models.option_quote import OptionQuote
from src.market_data.models.volatility_surface import VolatilitySurfaceBuilder
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider

@dataclass
class MarketDataService:
    provider: BaseMarketDataProvider
    ticker: str
    valuation_at: datetime = field(default_factory=datetime.now)
    min_quotes_per_smile: int = 4
    # calibrate spot and carry to the option market through put-call parity
    use_parity: bool = True
    max_carry_gap: float = 0.05

    def get_spot(self):
        spot_df = self.provider.fetch_spot(
            self.ticker,
            start=self.valuation_at - timedelta(days=10),
            end=self.valuation_at + timedelta(days=1)
        )

        if spot_df is None:
            raise TickerNotFoundError(f"No market data found for ticker {self.ticker!r}")

        self.spot = load_spot(spot_df, self.valuation_at)
        self.quoted_spot = self.spot
        self.spot_source = "quoted"
    
    def get_yield_curve(self):
        raw_rates = self.provider.fetch_rate()
        rates = build_rate_curve(self.valuation_at, raw_rates)
        self.yield_curve = YieldCurve(rates)

    def get_dividend_curve(self):
        # None means the ticker pays no dividends
        self.raw_dividends = self.provider.fetch_dividend(self.ticker)

        q = build_dividend_yield(self.raw_dividends, self.spot, self.valuation_at)

        self.dividend_curve = DividendCurve(None, None, q)
        self.dividend_source = "trailing dividends"

    def get_option_quotes(self) -> list[OptionQuote]:
        self.option_quotes: list[OptionQuote] = get_all_option_quotes(self.provider, self.ticker, self.valuation_at)
        return self.option_quotes

    def get_implied_spot(self):
        """
        Replace the quoted spot by the spot implied from put-call parity on the option quotes.
        The equity feed and the option chain are not synchronised; the options are what we calibrate to.
        Keeps the quoted spot when there are not enough reliable call/put pairs (e.g. market closed).
        """
        parity = ImpliedSpotFromParity()
        dividend_curve = self.dividend_curve
        spot = self.quoted_spot

        # the dividend yield is a ratio to the spot and enters parity: iterate spot -> q -> spot
        for _ in range(5):
            implied_spot = parity.get_spot(
                option_quotes=self.option_quotes,
                quoted_spot=self.quoted_spot,
                yield_curve=self.yield_curve,
                dividend_curve=dividend_curve
            )

            if implied_spot is None:
                return

            q = build_dividend_yield(self.raw_dividends, implied_spot, self.valuation_at)
            dividend_curve = DividendCurve(None, None, q)

            converged = abs(implied_spot - spot) < 1e-10 * implied_spot
            spot = implied_spot
            if converged:
                break

        self.spot = spot
        self.spot_source = "put-call parity"
        self.dividend_curve = dividend_curve

    def get_implied_carry(self):
        """
        Replace the dividend yield by the carry implied by each expiry's parity forward:
            F(T) = S e^{(r(T) - q(T)) T}   =>   q(T) = r(T) - ln(F(T) / S) / T
        q(T) then absorbs everything the option market prices into the forward and the inputs miss:
        stale or wrong rates, discrete dividends, borrow costs.
        Keeps the dividend-based yield when there is no reliable forward.
        """
        forwards = ImpliedSpotFromParity().implied_forwards(
            option_quotes=self.option_quotes,
            quoted_spot=self.spot,
            yield_curve=self.yield_curve
        )

        dividend_q = self.dividend_curve.q(1.0)
        times, carries = [], []

        for T, forward in forwards.items():
            q = self.yield_curve.r(T) - np.log(forward / self.spot) / T

            # a carry far from the dividend yield means bad quotes, not a carry
            if abs(q - dividend_q) > self.max_carry_gap:
                continue

            times.append(float(T))
            carries.append(float(q))

        if not times:
            return

        if len(times) == 1:
            self.dividend_curve = DividendCurve(None, None, carries[0])
        else:
            self.dividend_curve = DividendCurve(None, times, carries)

        self.dividend_source = "put-call parity"

    def get_iv(self):
        if not hasattr(self, "option_quotes"):
            self.get_option_quotes()

        option_quotes_list = filter_quotes(self.option_quotes, self.spot)

        implied_volatilities: list[IVQuote] = []
        iv_solver = ImpliedVolatilityBS()

        for quote in option_quotes_list:
            # a single stale or arbitrageable quote must not kill the whole surface
            try:
                iv_quote = iv_solver.get_vol(
                    option_quote=quote,
                    spot=self.spot,
                    yield_curve=self.yield_curve,
                    dividend_curve=self.dividend_curve
                )
            except ValueError:
                continue

            if 0.01 < iv_quote.iv < 3.0:
                implied_volatilities.append(iv_quote)

        if not implied_volatilities:
            raise MarketDataUnavailableError(f"No usable option quotes to build a volatility surface for {self.ticker}")

        self.implied_volatilities = implied_volatilities

        return implied_volatilities
    
    def get_maturities_from_iv(self) -> list[float]:
        """Get sorted unique maturities from implied volatilities."""
        if self.implied_volatilities is None:
            self.get_iv()
        return sorted(set(iv_quote.T for iv_quote in self.implied_volatilities))

    
    def get_iv_with_same_maturity(self, T: float) -> list[IVQuote]:
        """Filter implied volatilities by maturity."""
        if self.implied_volatilities is None:
            self.get_iv()
        return [iv_quote for iv_quote in self.implied_volatilities if abs(iv_quote.T - T) < 1e-6]
    
    def get_iv_with_same_strike(self, K: float) -> list[IVQuote]:
        """Filter implied volatilities by maturity."""
        if self.implied_volatilities is None:
            self.get_iv()
        return [iv_quote for iv_quote in self.implied_volatilities if abs(iv_quote.K - K) < 1e-6]

    def get_strikes_from_iv(self) -> list[float]:
        """Get sorted unique strikes from implied volatilities."""
        if self.implied_volatilities is None:
            self.get_iv()
        return sorted(set(iv_quote.K for iv_quote in self.implied_volatilities))

    

    def build_volatility_smiles(self):
        self.maturities = self.get_maturities_from_iv()
        smile_curves: dict[float, VolatilitySmileCurve] = {}
        for t in self.maturities:
            options = self.get_iv_with_same_maturity(t)

            # not enough points for a meaningful spline
            if len(options) < self.min_quotes_per_smile:
                continue

            builder = VolatilitySmileBuilder(
                options = options,
                T=t,
                spot=self.spot,
                dividend_curve=self.dividend_curve,
                yield_curve=self.yield_curve
            )
            vol_smile_curve: VolatilitySmileCurve = VolatilitySmileCurve(t, builder.curve, builder.forward)
            smile_curves[t] = vol_smile_curve

        return smile_curves
    
    def build_volatility_terms_structures(self) -> dict[float, VolatilityTermStructureCurve]:
        self.strikes = self.get_strikes_from_iv()

        term_structure_curves: dict[float, VolatilityTermStructureCurve] = {}

        for k in self.strikes:
            term_structure_builder = TermStructureBuilder(
                K=k,
                options=self.get_iv_with_same_strike(k),
            )
            term_structure_curves[k] = VolatilityTermStructureCurve(K=term_structure_builder.K, curve=term_structure_builder.curve)

        return term_structure_curves
    
    def build_volatility_surface(self):
        smiles = self.build_volatility_smiles()

        if not smiles:
            raise MarketDataUnavailableError(f"Not enough option quotes to build any volatility smile for {self.ticker}")

        # term structures are not used by the surface interpolation (and need >= 2 maturities per strike)
        self.volatility = VolatilitySurfaceBuilder(
            smiles=smiles,
            terms={},
            times=list(smiles.keys()),
            strikes=self.get_strikes_from_iv()
        )

    def get_market_data_snapshot(self) -> MarketDataSnapshot:
        self.get_spot()
        self.get_yield_curve()
        self.get_dividend_curve()
        self.get_option_quotes()
        if self.use_parity:
            self.get_implied_spot()
            self.get_implied_carry()
        self.get_iv()
        self.build_volatility_surface()
        market_data_snapshot: MarketDataSnapshot = MarketDataSnapshot(
            ticker=self.ticker,
            spot=self.spot,
            rate=self.yield_curve,
            sigma=self.volatility,
            dividend_yield=self.dividend_curve,
            timestamp=str(self.valuation_at),
            source="Yahoo Finance",
            quoted_spot=self.quoted_spot,
            spot_source=self.spot_source,
            dividend_source=self.dividend_source
        )

        return market_data_snapshot
