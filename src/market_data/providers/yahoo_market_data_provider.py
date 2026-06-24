from datetime import datetime
import os

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta

from src.core.config import read_config
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider


class YahooMarketDataProvider(BaseMarketDataProvider):

    def __init__(self):
        self._ticker = {}

    def _get_ticker(self, ticker: str):
        if ticker not in self._ticker:
            self._ticker[ticker] = yf.Ticker(ticker)
        return self._ticker[ticker]

    def fetch_rate(self) -> dict:
        path = read_config("paths", "raw_data_rates")

        dfs = {}

        for file in os.listdir(path):
            if file.endswith(".csv"):
                full_path = os.path.join(path, file)
                data = pd.read_csv(full_path, sep=",")

                maturity = file[0:-4]  # e.g. DGS10

                date = pd.to_datetime(data["date"]).iloc[-1].normalize()

                rate = float(pd.to_numeric(data.iloc[-1, -1]) / 100)

                df = pd.DataFrame(
                    {maturity: [rate]},
                    index=[date]
                )

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
        df = t.history(
            start=start,
            end=end,
            interval=interval,
            auto_adjust=False,
            actions=False
        )
        return df if not df.empty else None

    def fetch_dividend(self, ticker: str) -> pd.Series | None:
        t = self._get_ticker(ticker)
        div = t.dividends
        return div if not div.empty else None

    def fetch_options(self, ticker: str) -> list[str]:
        t = self._get_ticker(ticker)
        return list(t.options)

    def fetch_option_chain(self, ticker: str, date: str | datetime) -> pd.DataFrame:
        t = self._get_ticker(ticker)
        expiry = str(date)
        chain = t.option_chain(expiry)

        calls = chain.calls.copy()
        puts = chain.puts.copy()

        calls["option_type"] = "call"
        puts["option_type"] = "put"

        return pd.concat([calls, puts], ignore_index=False)