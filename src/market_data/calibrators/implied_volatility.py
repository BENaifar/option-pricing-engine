from dataclasses import dataclass, replace

from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.implied_vol_inversion_functs import price_fn_bs, price_fn_prime


@dataclass
class OptionQuote:
    K: float
    T: float
    price: float


class ImpliedVolatility:
    def get_vol(
        self,
        option_quote,
        spot,
        yield_curve: YieldCurve,
        dividend_curve: DividendCurve,
        sigma_init: float = 0.2,
        tolerance: float = 1e-8,
        max_iter: int = 100
    ) -> float:

        sigma = sigma_init

        for _ in range(max_iter):

            # Compute BS price
            model_price = price_fn_bs(
                spot,
                option_quote.K,
                yield_curve.r(option_quote.T),
                dividend_curve.q(option_quote.T),
                sigma,
                option_quote.T,
                option_quote.type
            )

            # Price error
            error = model_price - option_quote.price

            # Converged
            if abs(error) < tolerance:
                return sigma

            # Compute Vega
            vega = price_fn_prime(
                spot,
                option_quote.K,
                yield_curve.r(option_quote.T),
                dividend_curve.q(option_quote.T),
                sigma,
                option_quote.T
            )

            # Avoid division by zero
            if abs(vega) < 1e-8:
                raise ValueError(
                    "Vega too small. Newton-Raphson unstable."
                )

            # Newton-Raphson update
            sigma = sigma - error / vega

            # Safety clamp
            sigma = max(1e-4, sigma)

        raise ValueError(
            "Implied volatility did not converge."
        )

    def get_vols(
        self,
        option_quotes: list[OptionQuote],
        spot: float,
        yield_curve: YieldCurve,
        dividend_curve: DividendCurve,
        sigma_init: float = 0.2,
        tolerance: float = 1e-8,
        max_iter: int = 100
    ) -> list[float]:
        vols = []
        for i in range(0, len(option_quotes)):
            vol = self.get_vol(
                option_quotes[i],
                spot,
                yield_curve,
                dividend_curve,
                sigma_init,
                tolerance,
                max_iter
            )

            vols.append(vol)

        return vols
