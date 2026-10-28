from abc import ABC, abstractmethod

from src.models.base_model import BaseModel
from src.market_data.market_data_snapshot import MarketDataSnapshot

class BaseScheme(ABC):
    @abstractmethod
    def step(self, *args, **kwargs):
        raise NotImplementedError