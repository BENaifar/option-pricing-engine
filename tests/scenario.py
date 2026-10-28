from dataclasses import replace

from src.instruments.base_option import BaseOption
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.models.flat_volatility import FlatVolatility

def stress_market(market: MarketDataSnapshot, *, spot_mult=1.0, vol_mult=1.0, rate_shift=0.0, div_shift=0.0):
    return replace(
        market,
        spot=market.spot * spot_mult,
        sigma=FlatVolatility(market.sigma.get_vol(0, 0) * vol_mult),
        rate=YieldCurve(market.rate.r(0) + rate_shift),
        dividend_yield= DividendCurve(None, None, market.dividend_yield.q(0) + div_shift) 
    )

def stress_option(option: BaseOption, *, strike_mult=1.0):
    return replace(
        option,
        strike = option.strike * strike_mult
    )