from dataclasses import dataclass

from src.instruments.option_types import OptionType


@dataclass
class OptionQuote:
    K: float
    T: float
    price: float
    type: OptionType
    is_mid: bool = False  # True when price is a bid/ask mid, False for a lastPrice fallback