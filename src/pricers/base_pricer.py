from abc import ABC, abstractmethod

import numpy as np

from src.models.base_model import BaseModel
from src.instruments.base_option import BaseOption

class BasePricer(ABC):
    def __init__(self, model: BaseModel):
        self.model = model
    
    @abstractmethod
    def price(self, option: BaseOption) -> np.float64 | None:
        pass