from abc import ABC, abstractmethod

import numpy as np

from src.models.base_model import BaseModel
from src.instruments.base_option import BaseOption

class BasePricer(ABC):
    def __init__(self, model: BaseModel):
        self.model = model
    
    @abstractmethod
    def price(self, option: BaseOption) -> np.float64 | None:
        pass

    def supports_analytical_greeks(self) -> bool:
        return False
    
    def delta(self, option, market):
        raise NotImplementedError("No analytical Greeks implemented")
    
    def gamma(self, option, market):
        raise NotImplementedError("No analytical Greeks implemented")

    def vega(self, option, market):
        raise NotImplementedError("No analytical Greeks implemented")

    def theta(self, option, market):
        raise NotImplementedError("No analytical Greeks implemented")

    def rho(self, option, market):
        raise NotImplementedError("No analytical Greeks implemented")