from abc import ABC, abstractmethod

from src.models.base_model import BaseModel
from src.market_data.market_data import MarketData

class BaseScheme(ABC):

    @abstractmethod
    def step(self, model: BaseModel, market_data: MarketData, price, t, dt, brownian_increment):
        pass