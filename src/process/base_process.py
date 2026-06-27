from abc import ABC, abstractmethod

from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.models.volatility_model import VolatilityModel
from src.models.base_model import BaseModel


class StochasticProcess(ABC):        
    @abstractmethod
    def drift(self, S: float, t: float) -> float:
        pass
    
    @abstractmethod
    def diffusion(self, S: float, t: float, K: float) -> float:
        pass