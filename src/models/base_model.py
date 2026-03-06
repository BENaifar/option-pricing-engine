from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

@dataclass
class BaseModel(ABC):
    spot: float
    rate: float
    sigma: float
    n_steps: int

    def __post_init__(self):
        if self.n_steps <= 0:
            raise ValueError("Number of steps must be positive.")
        if self.spot <= 0:
            raise ValueError("Spot price must be positive.")
        if self.sigma <= 0:
            raise ValueError("Volatility must be positive.")


    @abstractmethod
    def simulate_paths(self, maturity, n_paths, seed=None) -> np.ndarray:
        pass