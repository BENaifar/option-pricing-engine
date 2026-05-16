from abc import ABC, abstractmethod

from src.models.base_model import BaseModel
from src.market_data.market_data_snapshot import MarketDataSnapshot

class BaseScheme(ABC):

    @abstractmethod
    def step(self, model: BaseModel, market_data: MarketDataSnapshot, price, t, dt, brownian_increment):
        pass