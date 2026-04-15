from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

@dataclass
class BaseModel(ABC):
    rate: float
    sigma: float
    dividend_yield: float = 0.0

    def __post_init__(self):
        if self.sigma <= 0:
            raise ValueError("Volatility must be positive.")
        if self.dividend_yield < 0:
            raise ValueError("Dividend yield must be positive")


    @abstractmethod
    def drift(self, S: float, t: float) -> float:
        pass

    @abstractmethod
    def diffusion(self, S, t) -> float:
        pass
