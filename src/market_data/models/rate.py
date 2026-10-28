from dataclasses import dataclass
from datetime import date


@dataclass
class Rate:
    time_to_maturity: float
    rate: float
    as_of: date | None = None
