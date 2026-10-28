
from src.market_data.models.volatility_model import VolatilityModel


class FlatVolatility(VolatilityModel):
    
    def __init__(self, sigma: float) -> None:
        super().__init__()
        self.sigma = sigma

    def get_vol(self, K, T) -> float:
        return self.sigma

    # @abstractmethod
    # def is_valid(self) -> bool:
    #     """Basic sanity check — did the fit succeed?"""
    #     pass