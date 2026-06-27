import numpy as np

from src.process.base_process import StochasticProcess
from src.schemes.base_scheme import BaseScheme


class BinomialTreeScheme(BaseScheme):
    def step(self, S: float, t: float, dt: float, K: float, process: StochasticProcess) -> tuple[float, float, float]:
        sigma = process.diffusion(S, t, K) / S
        mu = process.drift(S, t) / S

        u = np.exp(sigma * np.sqrt(dt))

        d = 1 / u

        a = np.exp(mu * dt)

        p = (a - d) / (u - d)

        return p, u, d
