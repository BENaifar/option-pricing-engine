from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from src.market_data.market_data_snapshot import MarketDataSnapshot

@dataclass
class BaseModel(ABC):

    @abstractmethod
    def drift(self, price: float, time: float, market_data: MarketDataSnapshot) -> float:
        pass

    @abstractmethod
    def diffusion(self, price: float, time:float, market_data: MarketDataSnapshot) -> float:
        pass
