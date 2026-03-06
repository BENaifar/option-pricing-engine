from dataclasses import dataclass

import numpy as np

from src.pricers.base_pricer import BasePricer
from src.models.base_model import BaseModel
from src.instruments.base_option import BaseOption

@dataclass
class MonteCarloPricer(BasePricer):
    model: BaseModel
    seed: int
    n_paths: int = 10000

    def __post_init__(self):
        if self.n_paths <= 0:
            raise ValueError("Number of simulations must be positive.")
    
    def price(self, option: BaseOption):
        paths = self.model.simulate_paths(option.maturity, self.n_paths, seed=self.seed)
        payoffs = option.payoff(paths[:, -1])
        discounted_price = np.exp(-self.model.rate * option.maturity) * np.mean(payoffs)
        
        return discounted_price
    
