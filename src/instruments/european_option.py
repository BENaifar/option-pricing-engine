from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption

@dataclass
class EuropeanOption(BaseOption):

    def payoff(self, ST) -> np.float64 | np.ndarray:
        if(self.option_type == 'put'):
            return np.maximum(self.strike - ST, 0)
        else:
            return np.maximum(ST - self.strike, 0)