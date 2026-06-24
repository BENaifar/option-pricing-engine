from dataclasses import dataclass
from datetime import datetime

from src.market_data.calibrators.implied_volatility import ImpliedVolatilityBS
from src.market_data.calibrators.volatility_smile_builder import VolatilitySmileBuilder
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.loaders.dividend_loader import build_dividend_curve_inputs
from src.market_data.loaders.rates_loader import build_rate_curve
from src.market_data.loaders.spot_loader import load_spot
from src.market_data.loaders.volatilityLoader import get_all_option_quotes
from src.market_data.models.iv_quote import IVQuote
from src.market_data.models.option_quote import OptionQuote
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

        return implied_volatilities
    

    # def _get_iv_quotes(self):
    #     iv_quotes_list = ImpliedVolatilityBS().get_vols(
    #         spot=self.spot,
    #         yield_curve=self.yield_curve,
    #         dividend_curve=self.divi
    #     )

    # def _get_vol_smile_curve(self):
    #     volatility_smile_builder = VolatilitySmileBuilder()
    
