from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.pricers.base_pricer import BasePricer
from src.instruments.base_option import BaseOption

class BlackScholesPricer(BasePricer):

    def _d1_d2(self, option: BaseOption):
        d1 = (np.log(self.model.spot / option.strike) + (self.model.rate + 0.5 * self.model.sigma ** 2) * option.maturity) / (self.model.sigma * np.sqrt(option.maturity))
        d2 = d1 - self.model.sigma * np.sqrt(option.maturity)

        return d1, d2

    def price(self, option) -> (np.float64):
        d1, d2 = self._d1_d2(option)

        if (option.option_type == "call"):
            price = self.model.spot * norm.cdf(d1) - option.strike * np.exp((-self.model.rate) * option.maturity) * norm.cdf(d2)
            return price
        else:
            price = option.strike * np.exp((-self.model.rate) * option.maturity) * norm.cdf(-d2) - self.model.spot * norm.cdf(-d1)
            return price