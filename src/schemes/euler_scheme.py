from src.process.base_process import StochasticProcess
from src.schemes.base_scheme import BaseScheme

class EulerScheme(BaseScheme): 
    def step(self, process: StochasticProcess, price, t, K, dt, brownian_increment) -> float:
        return price + process.drift(price, t) * dt + process.diffusion(price, t, K) * brownian_increment