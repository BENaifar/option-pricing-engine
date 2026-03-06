from abc import ABC, abstractmethod

from src.models.base_model import BaseModel
from src.instruments.base_option import BaseOption
from src.market_data.market_data import MarketData

class BasePricer(ABC):
    def __init__(self, model: BaseModel):
        self.model = model
    
    @abstractmethod
    def price(self, option: BaseOption, market_data: MarketData) -> float:
        pass

    @abstractmethod
    def greeks(self, option: BaseOption, market_data: MarketData) -> dict[str, float] | None:
        pass