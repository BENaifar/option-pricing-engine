from datetime import datetime

import numpy as np
import pandas as pd

from src.market_data.implied_vol_inversion_functs import price_fn_bs
from src.market_data.loaders.rates_loader import MATURITY_MAP
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider

# synthetic market used by the offline market data tests
VALUATION_DATE = datetime(2026, 1, 15, 16, 0)
SPOT = 100.0
RATE = 0.04
QUARTERLY_DIVIDEND = 0.25
EXPIRIES = ["2026-01-15", "2026-02-20", "2026-04-17", "2026-07-17", "2027-01-15"]
# denser near the money, like real chains
STRIKES = sorted([float(k) for k in range(60, 145, 5)] + [97.5, 102.5])


def true_vol(K: float) -> float:
    """Known smile the synthetic option prices are generated from."""
    m = np.log(K / SPOT)
    return float(0.22 - 0.05 * m + 0.15 * m ** 2)


def dividend_yield() -> float:
    return float(np.log1p(4 * QUARTERLY_DIVIDEND / SPOT))


class FakeMarketDataProvider(BaseMarketDataProvider):
    """
    Offline provider with the same output formats as YahooMarketDataProvider:
    tz-aware price history, FRED-like rate frames (decimal), yfinance-like dividends and chains.
    """

    def __init__(
        self,
        pays_dividends: bool = True,
        garbage_quote: bool = False,
        empty_spot: bool = False,
        spot_feed_offset: float = 0.0,
        has_bid_ask: bool = True
    ):
        self.pays_dividends = pays_dividends
        self.garbage_quote = garbage_quote
        self.empty_spot = empty_spot
        # equity feed out of sync with the options, which are always priced off SPOT
        self.spot_feed_offset = spot_feed_offset
        # False mimics a closed market: bid = ask = 0, only lastPrice
        self.has_bid_ask = has_bid_ask

    def fetch_spot(self, ticker, start=None, end=None, interval="1d"):
        if self.empty_spot:
            return None

        # the last bar is after the valuation date and must be ignored
        index = pd.DatetimeIndex(["2026-01-13", "2026-01-14", "2026-01-15", "2026-01-16"]).tz_localize("America/New_York")
        return pd.DataFrame({"Close": [98.0, 99.0, SPOT + self.spot_feed_offset, 250.0]}, index=index)

    def fetch_rate(self) -> dict:
        index = pd.DatetimeIndex(["2026-01-14", "2026-01-15", "2026-01-16"])
        return {
            name: pd.DataFrame({name: [RATE + 0.01, RATE, RATE + 0.02]}, index=index)
            for name in MATURITY_MAP
        }

    def fetch_dividend(self, ticker):
        if not self.pays_dividends:
            return None

        # four dividends inside the trailing year, one older that must be ignored
        index = pd.DatetimeIndex(["2024-11-10", "2025-02-10", "2025-05-12", "2025-08-11", "2025-11-10"]).tz_localize("America/New_York")
        return pd.Series([5.0] + [QUARTERLY_DIVIDEND] * 4, index=index)

    def fetch_options(self, ticker) -> list[str]:
        return list(EXPIRIES)

    def fetch_option_chain(self, ticker, date) -> pd.DataFrame:
        T = (pd.to_datetime(date) - pd.to_datetime(VALUATION_DATE)).days / 365.0
        q = dividend_yield() if self.pays_dividends else 0.0

        rows = []
        for option_type in ("call", "put"):
            for K in STRIKES:
                price = price_fn_bs(SPOT, K, RATE, q, true_vol(K), T, option_type)
                bid_ask = price if self.has_bid_ask else 0.0
                rows.append({"strike": K, "bid": bid_ask, "ask": bid_ask, "lastPrice": price, "option_type": option_type})

        if self.garbage_quote:
            # an OTM call worth more than the stock: no implied vol exists
            rows.append({"strike": 127.5, "bid": 0.0, "ask": 0.0, "lastPrice": 150.0, "option_type": "call"})

        return pd.DataFrame(rows)
