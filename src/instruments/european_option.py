from dataclasses import dataclass

import numpy as np

from src.instruments.base_option import BaseOption

@dataclass
class EuropeanOption(BaseOption):
    
    def is_american(self) -> bool:
        return False