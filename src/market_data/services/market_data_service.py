from dataclasses import dataclass
from datetime import datetime

from src.market_data.calibrators.implied_volatility import ImpliedVolatilityBS
from src.market_data.calibrators.term_structure_builder import TermStructureBuilder
from src.market_data.calibrators.volatility_smile_builder import VolatilitySmileBuilder
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.volatility_smile_curve import VolatilitySmileCurve
from src.market_data.curves.volatility_term_structure_curve import VolatilityTermStructureCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.loaders.dividend_loader import build_dividend_curve_inputs
from src.market_data.loaders.rates_loader import build_rate_curve
from src.market_data.loaders.spot_loader import load_spot
from src.market_data.loaders.volatilityLoader import get_all_option_quotes, get_maturities, get_strikes
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.models.iv_quote import IVQuote
from src.market_data.models.option_quote import OptionQuote
from src.market_data.models.volatility_surface import VolatilitySurfaceBuilder
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider

@dataclass
class MarketDataService:
    provider: BaseMarketDataProvider
    ticker: str
    valuation_at: datetime = datetime.now()

    def get_spot(self):
        spot_df = self.provider.fetch_spot(self.ticker, self.valuation_at)

        if spot_df is None:
            raise ValueError("API returned no data (None)")

        self.spot = load_spot(spot_df, self.valuation_at)
    
    def get_yield_curve(self):
        raw_rates = self.provider.fetch_rate()
        rates = build_rate_curve(self.valuation_at, raw_rates)
        self.yield_curve = YieldCurve(rates)

    def get_dividend_curve(self):
        raw_dividends = self.provider.fetch_dividend(self.ticker)

        if raw_dividends is None:
            raise ValueError("There was an error fetching dividends from the provider. It returned None")
        
        issuance_dates, times, dividends = build_dividend_curve_inputs(raw_dividends, self.valuation_at)

        self.dividend_curve = DividendCurve(issuance_dates, times, dividends)

    def get_iv(self):
        option_quotes_list: list[OptionQuote] = get_all_option_quotes(self.provider, self.ticker, self.valuation_at)
        implied_volatilities: list[IVQuote] = ImpliedVolatilityBS().get_vols(
            option_quotes=option_quotes_list,
            spot=self.spot,
            yield_curve=self.yield_curve,
            dividend_curve=self.dividend_curve
        )

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
        return [iv_quote for iv_quote in self.implied_volatilities if iv_quote.T - T < 1e-6]
    
    def get_iv_with_same_strike(self, K: float) -> list[IVQuote]:
        """Filter implied volatilities by maturity."""
        if self.implied_volatilities is None:
            self.get_iv()
        return [iv_quote for iv_quote in self.implied_volatilities if iv_quote.K - K < 1e-6]

    def get_strikes_from_iv(self) -> list[float]:
        """Get sorted unique strikes from implied volatilities."""
        if self.implied_volatilities is None:
            self.get_iv()
        return sorted(set(iv_quote.K for iv_quote in self.implied_volatilities))

    

    def build_volatility_smiles(self):
        self.maturities = self.get_maturities_from_iv()
        smile_curves: dict[float, VolatilitySmileCurve] = {}
        for t in self.maturities:
            builder = VolatilitySmileBuilder(
                options = self.get_iv_with_same_maturity(t),
                T=t,
                spot=self.spot,
                dividend_curve=self.dividend_curve,
                yield_curve=self.yield_curve
            )
            vol_smile_curve: VolatilitySmileCurve = VolatilitySmileCurve(t, builder._get_spline())
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
        self.volatility = VolatilitySurfaceBuilder(
            smiles=self.build_volatility_smiles(),
            terms=self.build_volatility_terms_structures(),
            times=self.get_maturities_from_iv(),
            strikes=self.get_strikes_from_iv()
        )

    def get_market_data_snapshot(self) -> MarketDataSnapshot:
        self.get_spot()
        self.get_yield_curve()
        self.get_dividend_curve()
        self.get_iv()
        self.build_volatility_surface()
        market_data_snapshot: MarketDataSnapshot = MarketDataSnapshot(
            ticker=self.ticker,
            spot=self.spot,
            rate=self.yield_curve,
            sigma=self.volatility,
            dividend_yield=self.dividend_curve,
            timestamp=str(self.valuation_at),
            source="Yahoo Finance"
        )

        return market_data_snapshot
