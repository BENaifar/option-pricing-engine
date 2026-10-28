from dataclasses import dataclass
from datetime import datetime

from src.instruments.option_types import OptionType
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.implied_vol_inversion_functs import price_fn_bs
from src.market_data.models.volatility_model import VolatilityModel

@dataclass(frozen=True)
class MarketDataSnapshot:
    ticker: str
    spot: float
    rate: YieldCurve
    sigma: VolatilityModel
    dividend_yield: DividendCurve
    timestamp: str | None = str(datetime.now())
    source: str | None = None
    quoted_spot: float | None = None  # equity feed price, before any parity adjustment
    spot_source: str | None = None    # "quoted" or "put-call parity"
    dividend_source: str | None = None  # "trailing dividends" or "put-call parity" (implied carry curve)
