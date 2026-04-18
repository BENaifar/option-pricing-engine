from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.instruments.base_option import BaseOption
from src.market_data.market_data import MarketData
from src.pricers.base_pricer import BasePricer

@dataclass
class BlackScholesPricer(BasePricer):

    def _d1_d2(self, option: BaseOption, market_data: MarketData):
        d1 = (np.log(market_data.spot / option.strike) + (market_data.rate + 0.5 * market_data.sigma ** 2) * option.maturity) / (market_data.sigma * np.sqrt(option.maturity))
        d2 = d1 - market_data.sigma * np.sqrt(option.maturity)

        return d1, d2


    def price(self, option, market_data: MarketData) -> (np.float64):
        d1, d2 = self._d1_d2(option, market_data)

        if (option.option_type == "call"):
            price = market_data.spot * norm.cdf(d1) - option.strike * np.exp((-market_data.rate) * option.maturity) * norm.cdf(d2)
            return price
        else:
            price = option.strike * np.exp((-market_data.rate) * option.maturity) * norm.cdf(-d2) - market_data.spot * norm.cdf(-d1)
            return price