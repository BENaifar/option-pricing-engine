from dataclasses import replace

def stress_market(market, *, spot_mult=1.0, vol_mult=1.0, rate_shift=0.0, div_shift=0.0):
    return replace(
        market,
        spot=market.spot * spot_mult,
        sigma=market.sigma * vol_mult,
        rate=market.rate + rate_shift,
        dividend_yield=market.dividend_yield + div_shift
    )

def stress_option(option, *, strike_mult=1.0):
    return replace(
        option,
        strike = option.strike * strike_mult
    )