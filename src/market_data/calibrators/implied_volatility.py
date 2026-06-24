from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.implied_vol_inversion_functs import price_fn_bs, price_fn_prime
from src.market_data.models.iv_quote import IVQuote
from src.market_data.models.option_quote import OptionQuote

class ImpliedVolatilityBS:

    def get_vol(
        self,
        option_quote: OptionQuote,
        spot: float,
        yield_curve: YieldCurve,
        dividend_curve: DividendCurve,
        sigma_init: float = 0.2,
        tolerance: float = 1e-8,
        max_iter: int = 100
    ) -> IVQuote:

        sigma = sigma_init

        for _ in range(max_iter):

            model_price = price_fn_bs(
                spot,
                option_quote.K,
                yield_curve.r(option_quote.T),
                dividend_curve.q(option_quote.T),
                sigma,
                option_quote.T,
                option_quote.type
            )

            error = model_price - option_quote.price

            if abs(error) < tolerance:
                return IVQuote(
                    K=option_quote.K,
                    T=option_quote.T,
                    iv=sigma,
                    option_type=option_quote.type
                )

            vega = price_fn_prime(
                spot,
                option_quote.K,
                yield_curve.r(option_quote.T),
                dividend_curve.q(option_quote.T),
                sigma,
                option_quote.T
            )

            if abs(vega) < 1e-8:
                raise ValueError(
                    f"Vega too small for K={option_quote.K}, "
                    f"T={option_quote.T}"
                )

            sigma -= error / vega

            sigma = max(1e-4, sigma)

        raise ValueError(
            f"Implied volatility did not converge for "
            f"K={option_quote.K}, T={option_quote.T}"
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
    ) -> list[IVQuote]:

        return [
            self.get_vol(
                option_quote=q,
                spot=spot,
                yield_curve=yield_curve,
                dividend_curve=dividend_curve,
                sigma_init=sigma_init,
                tolerance=tolerance,
                max_iter=max_iter
            )
            for q in option_quotes
        ]