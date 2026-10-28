import numpy as np

from src.process.base_process import StochasticProcess
from src.process.gbm_process import GBMProcess
from src.schemes.base_scheme import BaseScheme
from src.models.base_model import BaseModel
from src.market_data.market_data_snapshot import MarketDataSnapshot

class ExactGBMScheme(BaseScheme):
    def step(self, process: GBMProcess, price, t, K, dt, brownian_increment):
        return price * np.exp((process.r - process.q - 0.5 * process.sigma ** 2) * dt + process.sigma * brownian_increment)