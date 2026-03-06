from dataclasses import dataclass

from src.instruments.base_option import BaseOption

@dataclass
class EuropeanOption(BaseOption):

    def payoff(self, ST) -> float:
        if(self.option_type == 'put'):
                return max(self.strike - ST, 0)
        else:
            return max(ST - self.strike, 0)