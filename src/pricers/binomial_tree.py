from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from src.instruments.base_option import BaseOption
from src.market_data.market_data import MarketData
from src.pricers.base_pricer import BasePricer
from src.greeks.greeks import Greeks, GREEKS
from src.greeks.finite_differences_greeks import FiniteDifferencesGreeks
from src.greeks.finite_differences_bumper import FiniteDifferencesBumper

@dataclass
class BinomialTree(BasePricer):
    steps: int
    finite_differences_greeks: FiniteDifferencesGreeks
    finite_differences_bumper: FiniteDifferencesBumper

    def __post_init__(self):
        if self.steps <= 0:
            raise ValueError("Number of steps must be a positive integer.")

    def _u_d(self, option: BaseOption, market_data: MarketData) -> tuple[float, float]:
        u = np.exp(market_data.sigma * np.sqrt(option.maturity / self.steps))
        d = 1 / u
        return float(u), float(d)
    
    #To modify using models drift and diffusion for later time dependent calculations
    def calculate_probability(self, option: BaseOption, market_data: MarketData) -> float:
        u, d = self._u_d(option, market_data)
        return (np.exp((market_data.rate - market_data.dividend_yield) * (option.maturity / self.steps)) - d) / (u - d)

    def build_tree(self, option:BaseOption, market_data: MarketData) -> np.ndarray:
        u, d = self._u_d(option, market_data)

        tree = np.zeros((self.steps + 1, self.steps + 1))

        for i in range(self.steps + 1):
            j = np.arange(i + 1)
            tree[j, i] = market_data.spot * (u ** (i - j)) * (d ** j)
        
        return tree
    
    def build_european_payoff_tree(self, option: BaseOption, market_data: MarketData) -> np.ndarray:
        dt = option.maturity / self.steps
        probability = self.calculate_probability(option, market_data)

        tree = self.build_tree(option, market_data)
        option_payoffs = np.zeros((self.steps + 1, self.steps + 1))
        option_payoffs[:, -1] = option.payoff(tree[:, -1])

        for i in range(self.steps, 0, -1):
            j = np.arange(i)
            option_payoffs[j, i - 1] = np.exp(-market_data.rate * dt) * (probability * option_payoffs[j, i] + (1 - probability) * option_payoffs[j + 1, i])
        
        return option_payoffs
    
    def build_american_payoff_tree(self, option: BaseOption, market_data: MarketData) -> np.ndarray:
        dt = option.maturity / self.steps
        probability = self.calculate_probability(option, market_data)

        tree = self.build_tree(option, market_data)
        option_payoffs = np.zeros((self.steps + 1, self.steps + 1))
        option_payoffs[:, -1] = option.payoff(tree[:, -1])

        for i in range(self.steps, 0, -1):
            j = np.arange(i)
            new_payoff = np.exp(-market_data.rate * dt) * (probability * option_payoffs[j, i] + (1 - probability) * option_payoffs[j + 1, i])
            option_payoffs[j, i - 1] = np.maximum(option.payoff(tree[j , i - 1]), new_payoff)
        
        return option_payoffs
    
    def price(self, option: BaseOption, market_data: MarketData) -> np.float64:
        if option.is_american():
            return self.build_american_payoff_tree(option, market_data)[0, 0]
        return self.build_european_payoff_tree(option, market_data)[0, 0]
    
    def greeks(self, option: BaseOption, market_data: MarketData, greeks_list: list | None) -> Greeks:
        required = self._validate_required(greeks_list=greeks_list)

        greeks_values: Dict[str, Optional[float]] = {
            'delta': None,
            'gamma': None,
            'theta': None,
            'vega': None,
            'rho': None
        }

        if GREEKS.DELTA in required or GREEKS.GAMMA in required:
            greeks_values['delta'], greeks_values['gamma'] = self._spot_greeks(option, market_data)

        if GREEKS.THETA in required:
            greeks_values['theta'] = self._theta(option, market_data)

        if GREEKS.VEGA in required:
            greeks_values['vega'] = self._vega(option, market_data)

        if GREEKS.RHO in required:
            greeks_values['rho'] = self._rho(option, market_data)
            
        return Greeks(**greeks_values)

    def _rho(self, option: BaseOption, market_data: MarketData) -> float:
        rate_up, rate_down = self.finite_differences_bumper.bump_rate(market_data)

        price_rate_up = self.price(option, rate_up)
        price_rate_down = self.price(option, rate_down)

        rho = self.finite_differences_greeks.rho(price_rate_up, price_rate_down)

        return rho

    def _vega(self, option: BaseOption, market_data: MarketData) -> float:
        volatility_up, volatility_down = self.finite_differences_bumper.bump_volatility(market_data)

        price_vol_incr = self.price(option, volatility_up)
        price_vol_decr = self.price(option, volatility_down)

        vega = self.finite_differences_greeks.vega(price_vol_incr, price_vol_decr)

        return vega

    def _theta(self, option: BaseOption, market_data: MarketData) -> float:
        dt, option_short, option_long = self.finite_differences_bumper.bump_time(option)

        price_short = self.price(option_short, market_data)
        price_long = self.price(option_long, market_data)

        theta = self.finite_differences_greeks.theta(dt, price_short, price_long)

        return theta

    def _spot_greeks(self, option: BaseOption, market_data: MarketData) -> tuple[float, float]:
        base_price = self.price(option, market_data)

        market_down, market_up = self.finite_differences_bumper.bump_spot(market_data)

        price_up = self.price(option, market_up)
        price_down = self.price(option, market_down)

        delta = self.finite_differences_greeks.delta(market_data, price_up, price_down)
        gamma = self.finite_differences_greeks.gamma(market_data, base_price, price_up, price_down)

        return delta, gamma



