from dataclasses import dataclass, field

@dataclass
class Option:
    spot: float
    strike: float
    maturity: float
    sigma: float
    risk_free_rate: float
    option_type: str = field(default='call')

    def __post_init_(self):
        if self.spot <= 0:
            raise ValueError("Spot price must be positive.")
        if self.strike <= 0:
            raise ValueError("Strike price must be positive.")
        if self.maturity <= 0:
            raise ValueError("Maturity must be positive.")
        if self.sigma <= 0:
            raise ValueError("Volatility must be positive.")
        if self.option_type.lower() not in ("call", "put"):
            raise ValueError("Option must be 'call' or 'put'.")
        self.option_type = self.option_type.lower()

    def payoff(self, ST:float) -> float | None:
        if(self.option_type == 'put'):
            return max(self.strike - ST, 0)
        else:
            return max(ST - self.strike, 0)
