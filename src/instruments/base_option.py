from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import numpy as np

from src.instruments.option_types import OptionType

@dataclass
class BaseOption(ABC):
    strike: float
    maturity: float
    option_type: OptionType

    def __post_init__(self):
        if self.strike <= 0:
            raise ValueError("Strike price must be positive.")
        if self.maturity <= 0:
            raise ValueError("Maturity must be positive.")
        if isinstance(self.option_type, OptionType):
            raise ValueError("Option must be 'call' or 'put'.")

    def payoff(self, ST: np.float64 | np.ndarray) -> np.float64 | np.ndarray:
        if(self.option_type == 'put'):
            return np.maximum(self.strike - ST, 0)
        else:
            return np.maximum(ST - self.strike, 0)
        
    @abstractmethod
    def is_american(self) -> bool:
        pass        
        
