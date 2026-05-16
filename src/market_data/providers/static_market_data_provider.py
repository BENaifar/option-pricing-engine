from dataclasses import dataclass

from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider


@dataclass
class StaticMarketDataProvider(BaseMarketDataProvider):
    data: dict

    def fetch(self, ticker: str) -> dict:
        return self.data 
