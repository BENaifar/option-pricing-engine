from abc import ABC, abstractmethod

import pandas as pd

class BaseMarketDataProvider(ABC):

    @abstractmethod
    def fetch(self, ticker: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def fetch_spot(self, ticker: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def fetch_rate(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def fetch_dividend(self, ticker:str) -> pd.DataFrame:
        pass