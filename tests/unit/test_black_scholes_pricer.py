import pytest

def test_known_call_option(
    european_option_factory,
    black_scholes_model_factory,
    black_scholes_pricer_factory,
    benchmark_bs_call_case,
    abs_tol
):
    option = european_option_factory(
        strike=benchmark_bs_call_case["strike"],
        maturity=benchmark_bs_call_case["maturity"],
        option_type="call"
    )

    model = black_scholes_model_factory(
        rate=benchmark_bs_call_case['rate'],
        sigma=benchmark_bs_call_case['sigma'],
        dividend_yield=benchmark_bs_call_case['dividend_yield']
    )

    pricer = black_scholes_pricer_factory(model)
    price = float(pricer.price(option, benchmark_bs_call_case["spot"]))

    expected = benchmark_bs_call_case["expected_price"]

    assert price == pytest.approx(expected, abs=abs_tol)

