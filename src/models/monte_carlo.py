from dataclasses import dataclass

import numpy as np

from src.models.option import Option

@dataclass
class MonteCarlo:
    option: Option
    num_simulations: int = 10000

    def __post_init_(self):
        if self.num_simulations <= 0:
            raise ValueError("Number of simulations must be positive.")

    def simulate_gbm(self, n_steps=100):
        dt = self.option.maturity / n_steps
        Z = np.random.normal(0, 1, size=(self.num_simulations, n_steps))
        increments = (self.option.risk_free_rate - 0.5 * self.option.sigma ** 2) * dt + self.option.sigma * Z * np.sqrt(dt)
        B = np.cumsum(increments, axis=1)
        S_paths = self.option.spot * np.exp(B)

        return S_paths
    
    def compute_payoff(self, S_paths):
        ST = S_paths[:, -1]
        payoffs = np.vectorize(self.option.payoff)(ST)
        return payoffs
    
    def price_option(self, S_paths):
        payoffs = self.compute_payoff(S_paths)
        discounted_price = np.exp(-self.option.risk_free_rate * self.option.maturity) * np.mean(payoffs)
        return discounted_price
    
