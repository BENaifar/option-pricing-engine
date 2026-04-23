from src.numerics.base_scheme import BaseScheme
from src.models.base_model import BaseModel
from src.market_data.market_data import MarketData

class EulerScheme(BaseScheme):
    def step(self, model: BaseModel, market_data: MarketData, price, t, dt, brownian_increment):
        return price + model.drift(price, t, market_data) * dt + model.diffusion(price, t, market_data) * brownian_increment