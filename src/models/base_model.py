from abc import ABC
from dataclasses import dataclass

from src.market_data.market_data_snapshot import MarketDataSnapshot

@dataclass(frozen=True)
class BaseModel(ABC):
    market_data: MarketDataSnapshot

