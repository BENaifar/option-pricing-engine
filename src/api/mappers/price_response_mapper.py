from src.api.schemas import GreeksResponse, MonteCarloStatisticsResponse, PricerResultResponse, PriceResponse
from src.greeks.greeks import Greeks
from src.pipeline.pricing_pipeline import PricerResult, PricingResult
from src.pricers.monte_carlo_price_statistics import MonteCarloPriceStatistics


def price_response_from_result(result: PricingResult) -> PriceResponse:
    return PriceResponse(
        ticker=result.ticker,
        spot=result.spot,
        quoted_spot=result.quoted_spot,
        spot_source=result.spot_source,
        strike=result.strike,
        maturity=result.maturity,
        option_type=result.option_type,
        style=result.style,
        rate=result.rate,
        dividend_yield=result.dividend_yield,
        volatility=result.volatility,
        market_data_timestamp=result.market_data_timestamp,
        market_data_source=result.market_data_source,
        results=[_pricer_result(r) for r in result.results],
    )


def _pricer_result(result: PricerResult) -> PricerResultResponse:
    return PricerResultResponse(
        pricer=result.pricer,
        price=result.price,
        greeks=_greeks(result.greeks) if result.greeks else None,
        statistics=_statistics(result.statistics) if result.statistics else None,
    )


def _greeks(greeks: Greeks) -> GreeksResponse:
    return GreeksResponse(delta=greeks.delta, gamma=greeks.gamma, theta=greeks.theta, rho=greeks.rho, vega=greeks.vega)


def _statistics(statistics: MonteCarloPriceStatistics) -> MonteCarloStatisticsResponse:
    return MonteCarloStatisticsResponse(
        variance=statistics.variance,
        standard_deviation=statistics.standard_deviation,
        standard_error=statistics.standard_error,
        confidence_interval=statistics.confidence_interval,
        observations=statistics.observations,
    )
