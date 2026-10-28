import numpy as np
from scipy.stats import norm

from src.instruments.base_option import BaseOption
from src.instruments.option_types import OptionType
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.base_pricer import BasePricer
from src.process.base_process import StochasticProcess
from src.process.gbm_process import GBMProcess


class ClosedBlackScholesPricer(BasePricer):

    def price(self, option: BaseOption, process: StochasticProcess, spot: float) -> float:
        if type(process) is not GBMProcess:
            raise ValueError("You need to put in a GBMProcess")
        self.calculate_d1_d2(option, process, spot)
        self.calculate_norm_cdf()

        if option.option_type == OptionType.CALL:
            return spot * self.norm_cdf_d1 * np.exp(-process.q * option.maturity) - option.strike * np.exp(-process.r * option.maturity) * self.norm_cdf_d2
        return option.strike * np.exp(-process.r * option.maturity) * norm.cdf(-self._d2) - spot * np.exp(-process.q * option.maturity) * norm.cdf(-self._d1)
        
    def calculate_d1_d2(self, option: BaseOption, process: GBMProcess, spot: float):
        self._d1 = (np.log(spot/option.strike) + (process.r - process.q + ((process.sigma ** 2) / 2)) * option.maturity) / (process.sigma * np.sqrt(option.maturity))
        self._d2 = self._d1 - process.sigma * np.sqrt(option.maturity)

    def calculate_norm_cdf(self):
        self.norm_cdf_d1 = norm.cdf(self._d1)
        self.norm_cdf_d2 = norm.cdf(self._d2)
