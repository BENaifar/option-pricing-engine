from dataclasses import dataclass

@dataclass
class MarketData:
    spot: float
    rate: float
    sigma: float
    dividend_yield: float

    def __post_init__(self):
        if self.spot <= 0:
            raise ValueError("Spot price must be positive.")
        if self.sigma <= 0:
            raise ValueError("Volatility must be positive.")
        if self.dividend_yield < 0:
            raise ValueError("Dividend yield must be positive")