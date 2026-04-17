from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.instruments.base_option import BaseOption
from src.models.base_model import BaseModel

@dataclass
class BlackScholesPricer():
    model: BaseModel


    def _d1_d2(self, option: BaseOption, spot: float):
        d1 = (np.log(spot / option.strike) + (self.model.rate + 0.5 * self.model.sigma ** 2) * option.maturity) / (self.model.sigma * np.sqrt(option.maturity))
        d2 = d1 - self.model.sigma * np.sqrt(option.maturity)

        return d1, d2


    def price(self, option, spot) -> (np.float64):
        d1, d2 = self._d1_d2(option, spot)

        if (option.option_type == "call"):
            price = spot * norm.cdf(d1) - option.strike * np.exp((-self.model.rate) * option.maturity) * norm.cdf(d2)
            return price
        else:
            price = option.strike * np.exp((-self.model.rate) * option.maturity) * norm.cdf(-d2) - spot * norm.cdf(-d1)
            return price