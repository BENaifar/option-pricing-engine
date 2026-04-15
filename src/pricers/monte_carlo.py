from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption
from src.models.base_model import BaseModel
from src.schemes.base_scheme import BaseScheme

@dataclass
class MonteCarloPricer:
    model: BaseModel
    scheme : BaseScheme
    paths: int
    seed: int

    def __post_init__(self):
        if self.paths <= 0:
            raise ValueError("Paths can only be positive and over 0")
        if self.seed is None:
            raise ValueError("Seed must be provided")

    def simulate(self, option: BaseOption, spot: float, n_steps = 1000):
        rng = np.random.default_rng(self.seed)
        dt = option.maturity / n_steps
        dW = rng.normal(0, np.sqrt(dt), size=[self.paths, n_steps])
        
        S = np.full((self.paths, n_steps + 1), spot)
        for t in range(n_steps):
            S[:, t + 1] = self.scheme.step(self.model, S[:, t], t * dt, dt, dW[:, t])
        
        return S
    
    def price(self, option: BaseOption, spot, n_steps = 1000):
        paths = self.simulate(option, spot, n_steps)
        payoffs = option.payoff(paths[:, -1])
        # For now!!!
        discounted_price = np.mean(payoffs) * np.exp((-self.model.rate) * option.maturity)
        return discounted_price
    

    
