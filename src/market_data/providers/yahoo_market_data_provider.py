from datetime import datetime
import os

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta

from src.core.config import PROJECT_ROOT, read_config
from src.core.exceptions import MarketDataUnavailableError
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider


class YahooMarketDataProvider(BaseMarketDataProvider):

    def __init__(self):
        self._ticker = {}

    def _get_ticker(self, ticker: str):
        if ticker not in self._ticker:
            self._ticker[ticker] = yf.Ticker(ticker)
        return self._ticker[ticker]

    @staticmethod
    def _request(description: str, call):
        try:
            return call()
        except Exception as error:
            raise MarketDataUnavailableError(f"Yahoo Finance request failed ({description}): {error}") from error

    def fetch_rate(self) -> dict:
        path = PROJECT_ROOT / read_config("paths", "raw_data_rates")
        if not path.is_dir():
            raise MarketDataUnavailableError(f"Rate files not found in {path}")

        dfs = {}

        for file in os.listdir(path):
            if file.endswith(".csv"):
                full_path = os.path.join(path, file)
                data = pd.read_csv(full_path, sep=",")

                maturity = file[0:-4]  # e.g. DGS10

                # FRED files: DATE, <maturity>; missing values are "."
                rates = pd.to_numeric(data.iloc[:, -1], errors="coerce") / 100

                df = pd.DataFrame(
                    {maturity: rates.values},
                    index=pd.to_datetime(data.iloc[:, 0]).dt.normalize()
                ).dropna()

                dfs[maturity] = df

        return dfs
    
    def fetch_spot(
        self,
        ticker: str,
        start: datetime = datetime.now() - relativedelta(months=12),
        end: datetime = datetime.now(),
        interval: str = "1d"
    ) -> pd.DataFrame | None:
        t = self._get_ticker(ticker)
        df = self._request("price history", lambda: t.history(
            start=start,
            end=end,
            interval=interval,
            auto_adjust=False,
            actions=False
        ))
        return df if not df.empty else None

    def fetch_dividend(self, ticker: str) -> pd.Series | None:
        t = self._get_ticker(ticker)
        div = self._request("dividends", lambda: t.dividends)
        return div if not div.empty else None

    def fetch_options(self, ticker: str) -> list[str]:
        t = self._get_ticker(ticker)
        return list(self._request("option expiries", lambda: t.options))

    def fetch_option_chain(self, ticker: str, date: str | datetime) -> pd.DataFrame:
        t = self._get_ticker(ticker)
        expiry = str(date)
        chain = self._request(f"option chain {expiry}", lambda: t.option_chain(expiry))

        calls = chain.calls.copy()
        puts = chain.puts.copy()

        calls["option_type"] = "call"
        puts["option_type"] = "put"

        return pd.concat([calls, puts], ignore_index=False)