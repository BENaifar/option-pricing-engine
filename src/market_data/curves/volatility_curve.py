from dataclasses import dataclass

from src.instruments.european_option import EuropeanOption
from src.instruments.option_types import OptionType
from src.market_data.calibrators.implied_volatility import ImpliedVolatility
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.pricers.black_scholes import BlackScholesPricer

# flat yield curve for simplicity
class YieldCurve:
    def r(self, t):
        return 0.05

@dataclass
class VolatilityCurve:
    yield_curve: YieldCurve
    spot: float
    dividend_yield: float
    values: list[float]
    strikes: list[float]
    times: list[float]
    types: list[OptionType]

    def get_vols(self):
        iv = ImpliedVolatility()

        vols = []

        for i in range(0, len(self.strikes)):
            option = EuropeanOption(
                self.strikes[i],
                self.times[i],
                self.types[i]
            )

            market = MarketDataSnapshot(
                spot=self.spot,
                rate=self.yield_curve.r(self.times[i]),
                sigma = 0.1,
                dividend_yield=0       
            )

            vols.append(iv.get_vol(
                option=option,
                market=market,
                market_price=self.values[i],
                sigma_init=0.1
            ))

        return vols


if __name__ == "__main__":

    import math

    # --- 1. FIXED INPUTS ---
    spot = 100.0
    dividend_yield = 0.0

    strikes = [90.0, 100.0, 110.0, 120.0]
    times = [0.5, 1.0, 1.5, 2.0]
    types = [OptionType.CALL] * 4

    # TRUE vol curve (what we try to recover)
    true_vols = [0.20, 0.25, 0.22, 0.30]



    yield_curve = YieldCurve()

    # --- 2. PRICE GENERATION (synthetic market data) ---
    bs = BlackScholesPricer()

    values = []

    for i in range(len(strikes)):

        option = EuropeanOption(
            strike=strikes[i],
            maturity=times[i],
            option_type=types[i]
        )

        market = MarketDataSnapshot(
            spot=spot,
            rate=yield_curve.r(times[i]),
            dividend_yield=dividend_yield,
            sigma=true_vols[i]
        )

        price = bs.price(option, market)

        values.append(price)

    values = [i * 1.01 for i in values]

    # --- 3. BUILD CURVE OBJECT ---
    vol_curve = VolatilityCurve(
        yield_curve=yield_curve,
        spot=spot,
        dividend_yield=dividend_yield,
        strikes=strikes,
        times=times,
        types=types,
        values=values
    )

    # --- 4. RECOVER IMPLIED VOLATILITIES ---
    recovered = vol_curve.get_vols()

    # --- 5. PRINT RESULTS ---
    print("\nStrike | Time | True Vol | Implied Vol")
    print("-----------------------------------------")

    for i in range(len(strikes)):
        print(
            f"{strikes[i]:>6} | "
            f"{times[i]:>4} | "
            f"{true_vols[i]:>8.4f} | "
            f"{recovered[i]:>12.4f}"
        )

    # --- 6. ERROR CHECK ---
    errors = [
        abs(true_vols[i] - recovered[i])
        for i in range(len(true_vols))
    ]

    print("\nMax error:", max(errors))

