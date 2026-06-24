from abc import ABC, abstractmethod
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

class BaseMarketDataProvider(ABC):

    @abstractmethod
    def fetch_spot(self, ticker: str, start: datetime = datetime.now() - relativedelta(months=12), end: datetime = datetime.now(), interval: str = "1d") -> pd.DataFrame | None:
        pass

    @abstractmethod
    def fetch_rate(self) -> dict:
        pass

    @abstractmethod
    def fetch_dividend(self, ticker: str) -> pd.Series | None:
        pass

    @abstractmethod
    def fetch_options(self, ticker: str) -> list[str]:
        pass

    @abstractmethod
    def fetch_option_chain(self, ticker: str, date: str | datetime) -> pd.DataFrame:
        pass