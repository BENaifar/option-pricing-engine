from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption
from src.market_data.market_data import MarketData
from src.greeks.greeks import Greeks

@dataclass
class BasePricer(ABC):

    @abstractmethod
    def price(self, option: BaseOption, market_data: MarketData) -> (np.float64):
        pass

    @abstractmethod
    def greeks(self, option: BaseOption, market_data: MarketData, greeks_list: list | None) -> Greeks:
        pass