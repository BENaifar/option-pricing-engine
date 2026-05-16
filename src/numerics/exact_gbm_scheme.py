import numpy as np

from src.numerics.base_scheme import BaseScheme
from src.models.base_model import BaseModel
from src.market_data.market_data_snapshot import MarketDataSnapshot

class ExactGBMScheme(BaseScheme):
    def step(self, model: BaseModel, market_data: MarketDataSnapshot, price, t, dt, brownian_increment):
        return price * np.exp((market_data.rate - 0.5 * market_data.sigma ** 2) * dt + market_data.sigma * brownian_increment)