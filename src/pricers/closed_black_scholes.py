import numpy as np
from scipy.stats import norm

from src.instruments.base_option import BaseOption
from src.pricers.base_pricer import BasePricer
from src.process.base_process import StochasticProcess


class ClosedBlackScholesPricer(BasePricer):

    def price(self, option: BaseOption, process: StochasticProcess, spot: float) -> float:
        self.calculate_rate_and_vol(option, process, spot)
        self.calculate_d1_d2(option, spot)
        self.calculate_norm_cdf()

        if option.option_type == "call":
            return spot * self.norm_cdf_d1 - option.strike * np.exp(-self.r * option.maturity) * self.norm_cdf_d2
        return option.strike * np.exp(-self.r * option.maturity) * (1 - self.norm_cdf_d2) - spot * (1 - self.norm_cdf_d1)
        
    def calculate_d1_d2(self, option: BaseOption, spot: float):
        self._d1 = (np.log(spot/option.strike) + (self.r + self.sigma ** 2 / 2) * option.maturity) / self.sigma * np.sqrt(option.maturity)
        self._d2 = self._d1 - self.sigma * np.sqrt(option.maturity)

    def calculate_rate_and_vol(self, option: BaseOption, process: StochasticProcess, spot: float):
        self.r = process.drift(spot, option.maturity) / spot
        self.sigma = process.diffusion(spot, option.maturity, option.strike) / spot

    def calculate_norm_cdf(self):
        self.norm_cdf_d1 = norm.cdf(self._d1)
        self.norm_cdf_d2 = norm.cdf(self._d2)
