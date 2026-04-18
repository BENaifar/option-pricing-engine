from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption
from src.market_data.market_data import MarketData
from src.pricers.base_pricer import BasePricer

@dataclass
class BinomialTree(BasePricer):
    steps: int

    def __post_init__(self):
        if self.steps <= 0:
            raise ValueError("Number of steps must be a positive integer.")

    def _u_d(self, option: BaseOption, market_data: MarketData):
        u = np.exp(market_data.sigma * np.sqrt(option.maturity / self.steps))
        d = 1 / u
        return u, d
    
    #To modify using models drift and diffusion for later time dependent calculations
    def calculate_probability(self, option: BaseOption, market_data: MarketData) -> float:
        u, d = self._u_d(option, market_data)
        return (np.exp((market_data.rate - market_data.dividend_yield) * (option.maturity / self.steps)) - d) / (u - d)

    def build_tree(self, option:BaseOption, market_data: MarketData):
        u, d = self._u_d(option, market_data)

        tree = np.zeros((self.steps + 1, self.steps + 1))

        for i in range(self.steps + 1):
            j = np.arange(i + 1)
            tree[j, i] = market_data.spot * (u ** (i - j)) * (d ** j)
        
        return tree
    
    def build_european_payoff_tree(self, option: BaseOption, market_data: MarketData):
        dt = option.maturity / self.steps
        probability = self.calculate_probability(option, market_data)

        tree = self.build_tree(option, market_data)
        option_payoffs = np.zeros((self.steps + 1, self.steps + 1))
        option_payoffs[:, -1] = option.payoff(tree[:, -1])

        for i in range(self.steps, 0, -1):
            j = np.arange(i)
            option_payoffs[j, i - 1] = np.exp(-market_data.rate * dt) * (probability * option_payoffs[j, i] + (1 - probability) * option_payoffs[j + 1, i])
        
        return option_payoffs
    
    def build_american_payoff_tree(self, option: BaseOption, market_data: MarketData):
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
    
    def price(self, option: BaseOption, market_data: MarketData):
        if option.is_american():
            return self.build_american_payoff_tree(option, market_data)[0, 0]
        return self.build_european_payoff_tree(option, market_data)[0, 0]