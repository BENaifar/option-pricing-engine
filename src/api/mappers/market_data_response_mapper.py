from src.api.schemas import MarketDataResponse
from src.market_data.market_data_snapshot import MarketDataSnapshot

RATE_TENORS = (1 / 12, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
SURFACE_MONEYNESS = (0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2)
CARRY_TENOR = 1.0


def market_data_response_from_snapshot(snapshot: MarketDataSnapshot) -> MarketDataResponse:
    maturities = list(getattr(snapshot.sigma, "times", []))
    strikes = [round(moneyness * snapshot.spot, 2) for moneyness in SURFACE_MONEYNESS]

    return MarketDataResponse(
        ticker=snapshot.ticker,
        spot=snapshot.spot,
        quoted_spot=snapshot.quoted_spot,
        spot_source=snapshot.spot_source,
        timestamp=snapshot.timestamp,
        source=snapshot.source,
        rates={str(round(tenor, 4)): snapshot.rate.r(tenor) for tenor in RATE_TENORS},
        dividend_yield=snapshot.dividend_yield.q(CARRY_TENOR),
        dividend_source=snapshot.dividend_source,
        surface_maturities=maturities,
        surface_strikes=strikes,
        surface_vols=[[round(float(snapshot.sigma.get_vol(K, T)), 6) for K in strikes] for T in maturities],
    )
