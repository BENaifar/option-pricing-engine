from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.greeks.greeks import Greeks, GREEKS

@dataclass
class BasePricer(ABC):

    @abstractmethod
    def price(self, option: BaseOption, market_data: MarketDataSnapshot) -> float:
        pass

    @abstractmethod
    def greeks(self, option: BaseOption, market_data: MarketDataSnapshot, greeks_list: list | None = None) -> Greeks:
        pass

    def _validate_required(self, greeks_list):
        if greeks_list is None:
            greeks_list = [GREEKS.DELTA, GREEKS.GAMMA, GREEKS.THETA, GREEKS.RHO, GREEKS.VEGA]
        
        if not isinstance(greeks_list, list):
            raise TypeError(f"greeks_list must be a list or None, got {type(greeks_list).__name__}")
        
        for greek in greeks_list:
            if not isinstance(greek, GREEKS):
                raise ValueError(f"Invalid greek: {greek}. Must be one of {[g.name for g in GREEKS]}")
        
        required = set(greeks_list)
        return required        