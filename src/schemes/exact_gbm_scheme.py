import numpy as np

from src.schemes.base_scheme import BaseScheme
from src.models.base_model import BaseModel

class ExactGBMScheme(BaseScheme):
    def step(self, model: BaseModel, S, t, dt, brownian_increment):
        return S * np.exp((model.rate - 0.5 * model.sigma ** 2) * dt + model.sigma * brownian_increment)