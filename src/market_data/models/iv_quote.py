from dataclasses import dataclass

from src.instruments.option_types import OptionType


@dataclass(frozen=True)
class IVQuote:
    """An OptionQuote enriched with its computed implied vol."""
    K:           float
    T:           float
    iv:          float
    option_type: OptionType
    bid_iv:      float | None = None
    ask_iv:      float | None = None
