import numpy as np
from scipy.stats import norm

from src.models.option import Option

class BlackScholes:
    def __init__(self, option: Option):
        self.option = option

    def _d1_d2(self):
        d1 = (np.log(self.option.S0 / self.option.K) + (self.option.r + 0.5 * self.option.sigma ** 2) * self.option.T) / (self.option.sigma * np.sqrt(self.option.T))
        d2 = d1 - self.option.sigma * np.sqrt(self.option.T)

        return d1, d2


    def price(self) -> (np.float64):
        d1, d2 = self._d1_d2()

        if (self.option.option_type == "call"):
            C = self.option.S0 * norm.cdf(d1) - self.option.K * np.exp((-self.option.r) * self.option.T) * norm.cdf(d2)
            return C
        elif (self.option.option_type == "put"):
            C = self.option.K * np.exp((-self.option.r) * self.option.T) * norm.cdf(-d2) - self.option.S0 * norm.cdf(-d1)
            return C
        else:
            raise ValueError("Error occured")
        
    def delta(self):
        d1, _ = self._d1_d2()

        if (self.option.option_type == "call"):
            return norm.cdf(d1)
        
        elif (self.option.option_type == "put"):
            return norm.cdf(d1) - 1
        
        else:
            raise ValueError("Option types can only be: put or call")
    
    def gamma(self):
        d1, _ = self._d1_d2()

        return norm.pdf(d1) / (
            self.option.S0 * self.option.sigma * np.sqrt(self.option.T)
        )
    
    def vega(self):
        d1, _ = self._d1_d2()

        return self.option.S0 * norm.pdf(d1) * np.sqrt(self.option.T)
    
    def theta(self):
        d1, d2 = self._d1_d2()
        S0 = self.option.S0
        K = self.option.K
        T = self.option.T
        sigma = self.option.sigma
        r = self.option.r

        volatility_decay = - ((S0 * norm.pdf(d1) * sigma)
                   / (2 * np.sqrt(T)))
        
        if (self.option.option_type == 'call'):
            theta = volatility_decay - r * K * np.exp((-r) * T) * norm.cdf(d2)
            return theta

        elif (self.option.option_type == 'put'):
            theta = volatility_decay + r * K * np.exp((-r) * T) * norm.cdf(-d2)
            return theta
        
        else: 
            raise ValueError("Option types can only be: put or call")
        
    def rho(self):
        _, d2 = self._d1_d2()
        K = self.option.K
        T = self.option.T
        r = self.option.r

        if (self.option.option_type == "call"):
            return K * T * np.exp(-r * T) * norm.cdf(d2)
        
        elif (self.option.option_type == "put"):
            return -K * T * np.exp(-r * T) * norm.cdf(-d2)
        
        else:
            raise ValueError("Option types can only be: put or call")
