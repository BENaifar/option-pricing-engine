from dataclasses import dataclass

import numpy as np

from src.models.base_model import BaseModel

@dataclass
class MonteCarlo(BaseModel):
    num_simulations: int = 10000
    n_steps: int = 100

    def __post_init_(self):
        if self.num_simulations <= 0:
            raise ValueError("Number of simulations must be positive.")

    def simulate_path(self, option, market):
        dt = option.maturity / self.n_steps
        Z = np.random.normal(0, 1, size=(self.num_simulations, self.n_steps))
        increments = (market.risk_free_rate - 0.5 * market.sigma ** 2) * dt + market.sigma * Z * np.sqrt(dt)
        B = np.cumsum(increments, axis=1)
        S_paths = market.spot * np.exp(B)

        return S_paths
    
    def compute_payoff(self, option, S_paths):
        ST = S_paths[:, -1]
        payoffs = np.vectorize(option.payoff)(ST)
        return payoffs
    
    def price(self, option, market):
        S_paths = self.simulate_path(option, market)
        payoffs = self.compute_payoff(option, S_paths)
        discounted_price = np.exp(-market.risk_free_rate * option.maturity) * np.mean(payoffs)
        return discounted_price
    
