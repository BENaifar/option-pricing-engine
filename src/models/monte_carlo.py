from option import Option
import numpy as np

class MonteCarlo:
    def __init__(self, option: Option, num_simulations=10000):
        self.option = option
        self.num_simulations = num_simulations

    def simulate_gbm(self, n_steps=100):
        dt = self.option.T / n_steps
        Z = np.random.normal(0, 1, size=(self.num_simulations, n_steps))
        increments = (self.option.r - 0.5 * self.option.sigma ** 2) * dt + self.option.sigma * Z * np.sqrt(dt)
        B = np.cumsum(increments, axis=1)
        S_paths = self.option.S0 * np.exp(B)

        return S_paths
    
    def compute_payoff(self, S_paths):
        ST = S_paths[:, -1]
        payoffs = np.array([self.option.payoff(s) for s in ST])
        return payoffs
    
    def price_option(self, S_paths):
        payoffs = self.compute_payoff(S_paths)
        discounted_price = np.exp(-self.option.r * self.option.T) * np.mean(payoffs)
        return discounted_price
    
