import numpy as np
from scipy.stats import norm

from src.models.option import Option

class BlackScholes:
    def __init__(self, option: Option):
        self.option = option

    def price(self) -> (np.float64):
        d1 = (np.log(self.option.S0 / self.option.K) + (self.option.r + 0.5 * self.option.sigma ** 2) * self.option.T) / (self.option.sigma * np.sqrt(self.option.T))
        d2 = d1 - self.option.sigma * np.sqrt(self.option.T)
        if (self.option.option_type == "call"):
            C = self.option.S0 * norm.cdf(d1) - self.option.K * np.exp((-self.option.r) * self.option.T) * norm.cdf(d2)
            return C
        elif (self.option.option_type == "put"):
            C = self.option.K * np.exp((-self.option.r) * self.option.T) * norm.cdf(-d2) - self.option.S0 * norm.cdf(-d1)
            return C
        else:
            raise ValueError("Error occured")
        
