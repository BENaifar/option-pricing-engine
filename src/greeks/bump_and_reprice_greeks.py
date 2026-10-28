import copy
from dataclasses import dataclass, field, replace

import numpy as np

from src.greeks.finite_differences_greeks import FiniteDifferencesGreeks
from src.greeks.greeks import Greeks
from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.instruments.base_option import BaseOption
from src.pricers.base_pricer import BasePricer
from src.pricers.monte_carlo import MonteCarloPricer
from src.process.base_process import StochasticProcess


@dataclass
class BumpAndRepriceGreeks:
    """
    Pricer-agnostic finite-difference greeks.
    Bumps the spot, the option maturity, and the process parameters (sigma, r), then reprices.
    """
    greek_bumps_config: GreeksBumpsConfig = field(default_factory=GreeksBumpsConfig)

    def __post_init__(self):
        self.finite_differences_greeks = FiniteDifferencesGreeks(greek_bumps_config=self.greek_bumps_config)

    def compute(self, pricer: BasePricer, option: BaseOption, process: StochasticProcess, spot: float) -> Greeks:
        price = self._repricer(pricer, option)
        config = self.greek_bumps_config

        # delta / gamma: central differences on the spot
        h = config.spot_rel * spot
        base_price = price(option, process, spot)
        price_up = price(option, process, spot + h)
        price_down = price(option, process, spot - h)

        delta = (price_up - price_down) / (2 * h)
        gamma = (price_up - 2 * base_price + price_down) / h ** 2

        # vega
        vol_up = self._bump_process(process, "sigma", config.vol_abs)
        vol_down = self._bump_process(process, "sigma", -config.vol_abs)
        vega = self.finite_differences_greeks.vega(price(option, vol_up, spot), price(option, vol_down, spot))

        # rho
        rate_up = self._bump_process(process, "r", config.rate_abs)
        rate_down = self._bump_process(process, "r", -config.rate_abs)
        rho = self.finite_differences_greeks.rho(price(option, rate_up, spot), price(option, rate_down, spot))

        # theta (per year)
        dt = config.time_days
        option_short = replace(option, maturity=max(option.maturity - dt, 1e-8))
        option_long = replace(option, maturity=option.maturity + dt)
        theta = self.finite_differences_greeks.theta(dt, price(option_short, process, spot), price(option_long, process, spot))

        return Greeks(
            delta=float(delta),
            gamma=float(gamma),
            theta=float(theta),
            rho=float(rho),
            vega=float(vega)
        )

    @staticmethod
    def _bump_process(process: StochasticProcess, attribute: str, shift: float) -> StochasticProcess:
        bumped = copy.copy(process)
        setattr(bumped, attribute, getattr(process, attribute) + shift)
        return bumped

    @staticmethod
    def _repricer(pricer: BasePricer, option: BaseOption):
        if not isinstance(pricer, MonteCarloPricer):
            return pricer.price

        # common random numbers: every bumped price reuses the same normals,
        # otherwise the finite differences are dominated by Monte Carlo noise
        Z = pricer.rng.normal(0, 1, size=[pricer.paths, pricer.n_steps])

        def price(option: BaseOption, process: StochasticProcess, spot: float) -> float:
            return pricer.price(option, process, spot, Z)

        return price
