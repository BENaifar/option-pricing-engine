from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption
from src.models.base_model import BaseModel
from src.pricers.base_pricer import BasePricer
from src.schemes.base_scheme import BaseScheme
from src.market_data.market_data import MarketData

@dataclass
class MonteCarloPricer(BasePricer):
    model: BaseModel
    scheme : BaseScheme
    paths: int
    seed: int
    n_steps: int = 64
    

    def __post_init__(self):
        if self.paths <= 0 or not isinstance(self.paths, (int, np.integer)):
            raise ValueError("Paths can only be positive and over 0")
        if self.seed is None or self.seed < 0 or not isinstance(self.seed, (int, np.integer)):
            raise ValueError("Seed must be provided")

    def simulate(self, option: BaseOption, market_data: MarketData):
        rng = np.random.default_rng(self.seed)
        dt = option.maturity / self.n_steps
        brownian_increment = rng.normal(0, np.sqrt(dt), size=[self.paths, self.n_steps])
        
        S = np.full((self.paths, self.n_steps + 1), market_data.spot)
        for t in range(self.n_steps):
            S[:, t + 1] = self.scheme.step(self.model, market_data, S[:, t], t * dt, dt, brownian_increment[:, t])
        
        return S
    
    def price(self, option: BaseOption, market_data: MarketData):
        paths = self.simulate(option, market_data)
        payoffs = option.payoff(paths[:, -1])
        discounted_price = np.mean(payoffs) * np.exp((-market_data.rate) * option.maturity)
        return discounted_price
    

    
