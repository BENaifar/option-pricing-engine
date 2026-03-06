from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class BaseOption(ABC):
    strike: float
    maturity: float
    option_type: str = field(default='call')

    def __post_init_(self):
        if self.strike <= 0:
            raise ValueError("Strike price must be positive.")
        if self.maturity <= 0:
            raise ValueError("Maturity must be positive.")
        if self.option_type.lower() not in ("call", "put"):
            raise ValueError("Option must be 'call' or 'put'.")
        self.option_type = self.option_type.lower()

    @abstractmethod
    def payoff(self, ST:float) -> float | None:
        pass
