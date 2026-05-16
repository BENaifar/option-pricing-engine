from dataclasses import dataclass

from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider


@dataclass
class MarketDataService:

    provider: BaseMarketDataProvider

    def _spot(self, ticker: str):
        raw = self.provider.fetch(ticker)
        
        return 
    

