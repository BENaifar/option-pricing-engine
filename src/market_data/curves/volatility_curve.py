from dataclasses import dataclass

from src.instruments.option_types import OptionType
from src.market_data.calibrators.implied_volatility import ImpliedVolatilityBS
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.models.option_quote import OptionQuote

@dataclass
class VolatilityCurve:
    yield_curve: YieldCurve
    option_quotes: list[OptionQuote]
    spot: float
    dividend_yield: DividendCurve
    values: list[float]
    strikes: list[float]
    times: list[float]
    types: list[OptionType]
