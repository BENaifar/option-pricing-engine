from dataclasses import dataclass

from src.instruments.option_types import OptionType


@dataclass
class OptionQuote:
    K: float
    T: float
    price: float
    type: OptionType