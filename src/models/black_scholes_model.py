from dataclasses import dataclass
from src.models.base_model import BaseModel

@dataclass
class BlackScholesModel(BaseModel):

    def drift(self, price, time, market_data):
        return (market_data.rate - market_data.dividend_yield) * price
    
    def diffusion(self, price, time, market_data):
        return market_data.sigma * price