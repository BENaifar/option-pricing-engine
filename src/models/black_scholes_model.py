from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.models.base_model import BaseModel

class BlackScholesModel(BaseModel):

    def __init__(self, market_data: MarketDataSnapshot, strike:float, maturity: float) -> None:
        super().__init__(market_data=market_data)
        self.r: float = market_data.rate.r(maturity)
        self.q: float = market_data.dividend_yield.q(maturity)
        self.sigma: float = market_data.sigma.get_vol(strike, maturity)