from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.instruments.base_option import BaseOption
from src.market_data.market_data import MarketData

@dataclass
class BlackScholesPricer():
    market_data: MarketData

    def _d1_d2(self, option: BaseOption, spot: float):
        d1 = (np.log(spot / option.strike) + (self.market_data.rate + 0.5 * self.market_data.sigma ** 2) * option.maturity) / (self.market_data.sigma * np.sqrt(option.maturity))
        d2 = d1 - self.market_data.sigma * np.sqrt(option.maturity)

        return d1, d2


    def price(self, option, spot) -> (np.float64):
        d1, d2 = self._d1_d2(option, spot)

        if (option.option_type == "call"):
            price = spot * norm.cdf(d1) - option.strike * np.exp((-self.market_data.rate) * option.maturity) * norm.cdf(d2)
            return price
        else:
            price = option.strike * np.exp((-self.market_data.rate) * option.maturity) * norm.cdf(-d2) - spot * norm.cdf(-d1)
            return price