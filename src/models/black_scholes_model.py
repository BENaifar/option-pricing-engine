from dataclasses import dataclass
from base_model import BaseModel

@dataclass
class BlackScholesModel(BaseModel):

    def drift(self, S, t):
        return (self.rate - self.dividend_yield) * S
    
    def diffusion(self, S, t):
        return self.sigma * S