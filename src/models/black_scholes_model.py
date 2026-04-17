from dataclasses import dataclass
from src.models.base_model import BaseModel

@dataclass
class BlackScholesModel(BaseModel):

    def drift(self, price, market_data):
        return (rate - dividend_yield) * price
    
    def diffusion(self, price, sigma):
        return sigma * price