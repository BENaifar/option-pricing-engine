from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from src.market_data.market_data import MarketData

@dataclass
class BaseModel(ABC):

    @abstractmethod
    def drift(self, price: float, time: float, market_data: MarketData) -> float:
        pass

    @abstractmethod
    def diffusion(self, price: float, time:float, market_data: MarketData) -> float:
        pass
