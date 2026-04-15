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
    
    def probability(self, option: BaseOption):
        u, d = self._u_d(option)
        return (np.exp((self.r - self.q) * (option.maturity / self.steps)) - d) / (u - d)

    def build_tree(self, option:BaseOption):
        u, d = self._u_d(option)

        tree = np.zeros((self.steps + 1, self.steps + 1))

        for i in range(self.steps + 1):
            j = np.arange(i + 1)
            tree[j, i] = self.spot * (u ** (i - j)) * (d ** j)
        
        return tree
    
    # def price(self, option: BaseOption):
    #     tree = self.build_tree(option)
    #     option_values = np.zeros((self.steps + 1, self.steps + 1))
    #     option_values[:, self.steps] = option.payoff(tree[:, self.steps])

    #     for i in range(self.steps - 1, -1, -1):
    #         option_values[:i+1, i] = 

