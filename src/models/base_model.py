from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from src.market_data.market_data import MarketData

@dataclass
class BaseModel(ABC):

    @abstractmethod
    def drift(self, price, time, market_data) -> float:
        pass

    @abstractmethod
    def diffusion(self, price, market_data) -> float:
        pass
