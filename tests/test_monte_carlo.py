import numpy as np
import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer, VarianceReductionTechnique
from src.pricers.monte_carlo_price_statistics import calculate_price_statistics
from src.process.base_process import StochasticProcess
from src.process.process_factory import ProcessFactory
from src.schemes.euler_scheme import EulerScheme
from src.schemes.exact_gbm_scheme import ExactGBMScheme

euler_scheme = EulerScheme()
techniques = list(VarianceReductionTechnique)

# a correct estimator lands within 4 standard errors of the true price with probability > 99.99%
TOLERANCE_IN_STANDARD_ERRORS = 4


@pytest.fixture
def process(standard_market_with_dividend):
    return ProcessFactory.create(BlackScholesModel(standard_market_with_dividend, strike=100, maturity=1.0))


def _pricer(technique, paths=100_000, n_steps=128, seed=42, scheme=euler_scheme):
    return MonteCarloPricer(scheme=scheme, paths=paths, n_steps=n_steps, seed=seed, variance_reduction_technique=technique)


@pytest.mark.parametrize("technique", techniques, ids=[t.value for t in techniques])
@pytest.mark.parametrize("option_name", ["standard_call", "standard_put"])
def test_monte_carlo_matches_closed_form(request, process, standard_market_with_dividend, technique, option_name):
    option = request.getfixturevalue(option_name)
    spot = standard_market_with_dividend.spot

    statistics = _pricer(technique).price_with_statistics(option, process, spot)
    closed_form = ClosedBlackScholesPricer().price(option, process, spot)

    assert abs(statistics.price - closed_form) < TOLERANCE_IN_STANDARD_ERRORS * statistics.standard_error


@pytest.mark.parametrize("technique", techniques, ids=[t.value for t in techniques])
def test_monte_carlo_put_call_parity(process, standard_market_with_dividend, standard_call, standard_put, technique):
    """Call and put priced on the same normals: only the sampling error of the forward remains."""
    market, spot = standard_market_with_dividend, standard_market_with_dividend.spot
    pricer = _pricer(technique)
    Z = np.random.default_rng(7).normal(size=(pricer.paths, pricer.n_steps))

    call = pricer.price_with_statistics(standard_call, process, spot, Z)
    put = pricer.price_with_statistics(standard_put, process, spot, Z)

    T, K = standard_call.maturity, standard_call.strike
    parity = spot * np.exp(-market.dividend_yield.q(T) * T) - K * np.exp(-market.rate.r(T) * T)

    tolerance = TOLERANCE_IN_STANDARD_ERRORS * (call.standard_error + put.standard_error)
    assert call.price - put.price == pytest.approx(parity, abs=tolerance)


@pytest.mark.parametrize("technique", [VarianceReductionTechnique.ANTITHETIC, VarianceReductionTechnique.CONTROL_VARIATE])
def test_variance_reduction_lowers_the_standard_error(process, standard_market_with_dividend, standard_call, technique):
    spot = standard_market_with_dividend.spot

    plain = _pricer(VarianceReductionTechnique.NONE).price_with_statistics(standard_call, process, spot)
    reduced = _pricer(technique).price_with_statistics(standard_call, process, spot)

    assert reduced.standard_error < plain.standard_error


def test_antithetic_averages_each_path_with_its_mirror(process, standard_market_with_dividend, standard_call):
    spot = standard_market_with_dividend.spot
    pricer = _pricer(VarianceReductionTechnique.ANTITHETIC, paths=1_000, n_steps=4, scheme=ExactGBMScheme())
    Z = np.random.default_rng(3).normal(size=(pricer.paths, pricer.n_steps))

    discount = process.discount_factor(standard_call.maturity)
    up = standard_call.payoff(pricer.simulate(standard_call, process, spot, Z).terminal_paths)
    down = standard_call.payoff(pricer.simulate(standard_call, process, spot, -Z).terminal_paths)

    statistics = pricer.price_with_statistics(standard_call, process, spot, Z)

    assert statistics.price == pytest.approx(discount * np.mean((up + down) / 2), rel=1e-12)
    assert statistics.observations == pricer.paths


def test_control_variate_requires_a_gbm_process(standard_call):
    class OtherProcess(StochasticProcess):
        def drift(self, S, t): return 0.0 * S
        def diffusion(self, S, t, K): return 0.2 * S
        def discount_factor(self, t): return 1.0

    pricer = _pricer(VarianceReductionTechnique.CONTROL_VARIATE, paths=100, n_steps=2)

    with pytest.raises(ValueError, match="GBMProcess"):
        pricer.price_with_statistics(standard_call, OtherProcess(), 100.0)


def test_price_is_the_statistics_price(process, standard_market_with_dividend, standard_call):
    spot = standard_market_with_dividend.spot
    pricer = _pricer(VarianceReductionTechnique.ANTITHETIC, paths=1_000, n_steps=4)
    Z = np.random.default_rng(5).normal(size=(pricer.paths, pricer.n_steps))

    assert pricer.price(standard_call, process, spot, Z) == pricer.price_with_statistics(standard_call, process, spot, Z).price


def test_price_statistics_are_consistent(process, standard_market_with_dividend, standard_call):
    statistics = _pricer(VarianceReductionTechnique.NONE, paths=10_000).price_with_statistics(
        standard_call, process, standard_market_with_dividend.spot, confidence_level=0.99
    )
    low, high = statistics.confidence_interval

    assert statistics.observations == 10_000
    assert statistics.standard_deviation == pytest.approx(np.sqrt(statistics.variance))
    assert statistics.standard_error == pytest.approx(statistics.standard_deviation / np.sqrt(10_000))
    assert low < statistics.price < high
    assert (high - low) / 2 == pytest.approx(2.5763 * statistics.standard_error, rel=1e-3)


def test_calculate_price_statistics_on_known_values():
    statistics = calculate_price_statistics(np.array([1.0, 2.0, 3.0, 4.0]), confidence_level=0.95)

    assert statistics.price == 2.5
    assert statistics.variance == pytest.approx(5 / 3)
    assert statistics.standard_error == pytest.approx(np.sqrt(5 / 3) / 2)
    assert statistics.confidence_interval[1] - 2.5 == pytest.approx(3.1824 * statistics.standard_error, rel=1e-4)


@pytest.mark.parametrize("observations, confidence_level", [
    (np.array([1.0]), 0.95),
    (np.array([1.0, np.nan]), 0.95),
    (np.array([1.0, 2.0]), 1.0),
])
def test_calculate_price_statistics_rejects_invalid_input(observations, confidence_level):
    with pytest.raises(ValueError):
        calculate_price_statistics(observations, confidence_level=confidence_level)


def test_one_sample_t_test(process, standard_market_with_dividend, standard_call):
    spot = standard_market_with_dividend.spot
    statistics = _pricer(VarianceReductionTechnique.CONTROL_VARIATE).price_with_statistics(standard_call, process, spot)
    closed_form = ClosedBlackScholesPricer().price(standard_call, process, spot)

    assert not statistics.one_sample_t_test(closed_form, alpha=0.01)["reject_null"]
    assert statistics.one_sample_t_test(closed_form + 1.0, alpha=0.01)["reject_null"]
