from dataclasses import dataclass

import numpy as np

from src.models.base_model import BaseModel

@dataclass
class GBMModel(BaseModel):
            
    def simulate_paths(self, maturity, n_paths, seed=None):
        rng = np.random.default_rng(seed)
        dt = maturity / self.n_steps
        Z = rng.normal(0, dt, size=[n_paths, self.n_steps])
        increments = (self.rate - 0.5 * self.sigma ** 2) * dt + self.sigma * Z * np.sqrt(dt) 
        gbm = np.cumsum(increments, axis=1)
        S_paths = self.spot * np.exp(gbm)

        return S_paths
    
