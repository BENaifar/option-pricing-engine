from dataclasses import dataclass


@dataclass
class Rate:
    time_to_maturity: float  
    rate: float
