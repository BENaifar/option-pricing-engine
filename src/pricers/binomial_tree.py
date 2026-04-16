from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption

@dataclass
class BinomialTree:
    spot: float
    r: float
    sigma:float
    q: float
    steps: int

    def _u_d(self, option: BaseOption):
        u = np.exp(self.sigma * np.sqrt(option.maturity / self.steps))
        d = 1 / u
        return u, d
    
    def calculate_probability(self, option: BaseOption) -> float:
        u, d = self._u_d(option)
        return (np.exp((self.r - self.q) * (option.maturity / self.steps)) - d) / (u - d)

    def build_tree(self, option:BaseOption):
        u, d = self._u_d(option)

        tree = np.zeros((self.steps + 1, self.steps + 1))

        for i in range(self.steps + 1):
            j = np.arange(i + 1)
            tree[j, i] = self.spot * (u ** (i - j)) * (d ** j)
        
        return tree
    
    def build_european_payoff_tree(self, option: BaseOption):
        dt = option.maturity / self.steps
        probability = self.calculate_probability(option)

        tree = self.build_tree(option)
        option_payoffs = np.zeros((self.steps + 1, self.steps + 1))
        option_payoffs[:, -1] = option.payoff(tree[:, -1])

        for i in range(self.steps, 0, -1):
            j = np.arange(i)
            option_payoffs[j, i - 1] = np.exp(-self.r * dt) * (probability * option_payoffs[j, i] + (1 - probability) * option_payoffs[j + 1, i])
        
        return option_payoffs
    
    def build_american_payoff_tree(self, option: BaseOption):
        dt = option.maturity / self.steps
        probability = self.calculate_probability(option)

        tree = self.build_tree(option)
        option_payoffs = np.zeros((self.steps + 1, self.steps + 1))
        option_payoffs[:, -1] = option.payoff(tree[:, -1])

        for i in range(self.steps, 0, -1):
            j = np.arange(i)
            new_payoff = np.exp(-self.r * dt) * (probability * option_payoffs[j, i] + (1 - probability) * option_payoffs[j + 1, i])
            option_payoffs[j, i - 1] = np.maximum(option.payoff(tree[j , i - 1]), new_payoff)
        
        return option_payoffs
    
    def price(self, option: BaseOption):
        if option.is_american():
            return self.build_american_payoff_tree(option)[0, 0]
        return self.build_european_payoff_tree(option)[0, 0]