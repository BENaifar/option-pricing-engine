from dataclasses import dataclass

from src.instruments.option_types import OptionType


@dataclass(frozen=True)
class MarketQuote:
    K: float
    T: float
    option_type: OptionType
    bid: float
    ask: float

    @property
    def mid(self) -> float:
        return 0.5 * (self.bid + self.ask)

    @property
    def relative_spread(self) -> float:
        return (self.ask - self.bid) / self.mid

    def is_otm(self, spot: float) -> bool:
        if self.option_type == OptionType.PUT:
            return self.K < spot
        return self.K >= spot
