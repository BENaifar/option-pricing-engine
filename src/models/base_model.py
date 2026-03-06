from abc import ABC, abstractmethod
import numpy as np

class BaseModel(ABC):

    @abstractmethod
    def price(self, option, market) -> (np.float64):
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