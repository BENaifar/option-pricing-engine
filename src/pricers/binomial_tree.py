from dataclasses import dataclass, field

import numpy as np

from src.instruments.base_option import BaseOption
from src.pricers.base_pricer import BasePricer
from src.greeks.greeks import Greeks, GREEKS
from src.greeks.finite_differences_greeks import FiniteDifferencesGreeks
from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.market_data.market_bumper import MarketBumper
from src.process.base_process import StochasticProcess
from src.schemes.base_scheme import BaseScheme
from src.schemes.binomial_tree_scheme import BinomialTreeScheme

@dataclass
class BinomialTree(BasePricer):
    scheme: BinomialTreeScheme
    steps: int = 1000
    finite_differences_greeks: FiniteDifferencesGreeks = field(default_factory=lambda: FiniteDifferencesGreeks(greek_bumps_config=GreeksBumpsConfig()))
    finite_differences_bumper: MarketBumper = field(default_factory=lambda: MarketBumper(greek_bumps_config=GreeksBumpsConfig()))


    def __post_init__(self):
        if not isinstance(self.scheme, BaseScheme):
            raise TypeError("Not a scheme")
        
        if not isinstance(self.steps, (int, np.integer)) or self.steps <= 0:
            raise ValueError("Number of steps must be a positive integer.")
        
        if not isinstance(self.finite_differences_greeks, FiniteDifferencesGreeks):
            raise TypeError("finite_differences_greeks must be an instance of FiniteDifferencesGreeks")
        
        if not isinstance(self.finite_differences_bumper, MarketBumper):
            raise TypeError("finite_differences_bumper must be an instance of MarketBumper")

    def build_tree(self, option:BaseOption, process: StochasticProcess, spot: float) -> np.ndarray:
        tree = np.zeros((self.steps + 1, self.steps + 1))
        dt = option.maturity / self.steps

        _, u, d = self.scheme.step(spot, option.maturity, dt, option.strike, process)

        for i in range(self.steps + 1): 
            
            j = np.arange(i + 1)
            tree[j, i] = spot * (u ** (i - j)) * (d ** j)
        
        return tree
    
    def build_european_payoff_tree(self, option: BaseOption, process: StochasticProcess, spot: float) -> np.ndarray:
        dt = option.maturity / self.steps
        tree = self.build_tree(option, process, spot)
        option_payoffs = np.zeros((self.steps + 1, self.steps + 1))
        option_payoffs[:, -1] = option.payoff(tree[:, -1])

        p, _, _ = self.scheme.step(spot, option.maturity, dt, option.strike, process)

        for i in range(self.steps, 0, -1):
            j = np.arange(i)
            option_payoffs[j, i - 1] = process.discount_factor(dt) * (p * option_payoffs[j, i] + (1 - p) * option_payoffs[j + 1, i])
        
        return option_payoffs
    
    def build_american_payoff_tree(self, option: BaseOption, process: StochasticProcess, spot: float) -> np.ndarray:
        dt = option.maturity / self.steps

        tree = self.build_tree(option, process, spot)
        option_payoffs = np.zeros((self.steps + 1, self.steps + 1))
        option_payoffs[:, -1] = option.payoff(tree[:, -1])

        for i in range(self.steps, 0, -1):
            j = np.arange(i)
            p, _, _ = self.scheme.step(spot, dt * i, dt, option.strike, process)

            new_payoff = process.discount_factor(dt) * (p * option_payoffs[j, i] + (1 - p) * option_payoffs[j + 1, i])
            option_payoffs[j, i - 1] = np.maximum(option.payoff(tree[j , i - 1]), new_payoff)
        
        return option_payoffs
    
    def price(self, option: BaseOption, process: StochasticProcess, spot: float) -> float:
        if option.is_american():
            return self.build_american_payoff_tree(option, process, spot)[0, 0]
        return self.build_european_payoff_tree(option, process, spot)[0, 0]
    
    # def greeks(self, option: BaseOption, market_data: MarketDataSnapshot, greeks_list: list | None = None) -> Greeks:
    #     required = self._validate_required(greeks_list=greeks_list)

    #     greeks_values: Dict[str, Optional[float]] = {
    #         'delta': None,
    #         'gamma': None,
    #         'theta': None,
    #         'vega': None,
    #         'rho': None
    #     }

    #     if GREEKS.DELTA in required or GREEKS.GAMMA in required:
    #         greeks_values['delta'], greeks_values['gamma'] = self._spot_greeks(option, market_data)

    #     if GREEKS.THETA in required:
    #         greeks_values['theta'] = self._theta(option, market_data)

    #     if GREEKS.VEGA in required:
    #         greeks_values['vega'] = self._vega(option, market_data)

    #     if GREEKS.RHO in required:
    #         greeks_values['rho'] = self._rho(option, market_data)
            
    #     return Greeks(**greeks_values)

    # def _rho(self, option: BaseOption, market_data: MarketDataSnapshot) -> float:
    #     rate_up, rate_down = self.finite_differences_bumper.bump_rate(market_data)

    #     price_rate_up = self.price(option, rate_up)
    #     price_rate_down = self.price(option, rate_down)

    #     rho = self.finite_differences_greeks.rho(price_rate_up, price_rate_down)

    #     return rho

    # def _vega(self, option: BaseOption, market_data: MarketDataSnapshot) -> float:
    #     volatility_up, volatility_down = self.finite_differences_bumper.bump_volatility(market_data)

    #     price_vol_incr = self.price(option, volatility_up)
    #     price_vol_decr = self.price(option, volatility_down)

    #     vega = self.finite_differences_greeks.vega(price_vol_incr, price_vol_decr)

    #     return vega

    # def _theta(self, option: BaseOption, market_data: MarketDataSnapshot) -> float:
    #     dt, option_short, option_long = self.finite_differences_bumper.bump_time(option)

    #     price_short = self.price(option_short, market_data)
    #     price_long = self.price(option_long, market_data)

    #     theta = self.finite_differences_greeks.theta(dt, price_short, price_long)

    #     return theta

    # def _spot_greeks(self, option: BaseOption, market_data: MarketDataSnapshot) -> tuple[float, float]:
    #     base_price = self.price(option, market_data)

    #     market_down, market_up = self.finite_differences_bumper.bump_spot(market_data)

    #     price_up = self.price(option, market_up)
    #     price_down = self.price(option, market_down)

    #     delta = self.finite_differences_greeks.delta(market_data, price_up, price_down)
    #     gamma = self.finite_differences_greeks.gamma(market_data, base_price, price_up, price_down)

    #     return delta, gamma



