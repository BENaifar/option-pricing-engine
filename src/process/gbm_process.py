import numpy as np

from src.models.base_model import BaseModel
from src.models.black_scholes_model import BlackScholesModel
from src.process.base_process import StochasticProcess


class GBMProcess(StochasticProcess):

    def __init__(self, model: BlackScholesModel) -> None:
        super().__init__()
        self.r = model.r
        self.q = model.q
        self.sigma = model.sigma

    def drift(self, S: float, t: float) -> float:
        return S * (self.r - self.q)
    
    def diffusion(self, S: float, t: float, K: float) -> float:
        return S * self.sigma
    
    def discount_factor(self, t: float):
        return np.exp(-self.r * t)

    