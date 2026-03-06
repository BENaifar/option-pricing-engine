from dataclasses import dataclass

@dataclass
class MarketData:
    spot: float
    risk_free_rate: float
    sigma: float

    def __post_init_(self):
        if self.spot <= 0:
            raise ValueError("Spot price must be positive.")
        if self.sigma <= 0:
            raise ValueError("Volatility must be positive.")