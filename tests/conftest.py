# import math
# import random
# import pytest

# from src.instruments.american_option import AmericanOption
# from src.instruments.european_option import EuropeanOption

# from src.models.black_scholes_model import BlackScholesModel

# from src.pricers.black_scholes import BlackScholesPricer

# @pytest.fixture
# def abs_tol():
#     """
#     Absolute tolerance for deterministic pricing comparisons.
#     Example: closed-form vs benchmark.
#     """
#     return 1e-6


# @pytest.fixture
# def rel_tol():
#     """
#     Relative tolerance for larger values.
#     """
#     return 1e-4

# @pytest.fixture(autouse=True)
# def fixed_random_seed():
#     """
#     Ensures reproducibility for Monte Carlo tests.
#     Runs automatically for every test.
#     """
#     random.seed(42)

# # =========================================================
# # OPTION FACTORIES
# # =========================================================

# @pytest.fixture
# def european_option_factory():
#     def make(strike=100, maturity=1, option_type="call"):
#         return EuropeanOption(strike, maturity, option_type)
#     return make

# @pytest.fixture
# def american_option_factory():
#     def make(strike=100, maturity=1, option_type="call"):
#         return AmericanOption(strike, maturity, option_type)
#     return make


# # =========================================================
# # COMMON OPTION SCENARIOS
# # =========================================================

# @pytest.fixture
# def atm_call(european_option_factory):
#     return european_option_factory(
#         strike=100,
#         maturity=1.0,
#         option_type="call"
#     )


# @pytest.fixture
# def atm_put(european_option_factory):
#     return european_option_factory(
#         strike=100,
#         maturity=1.0,
#         option_type="put"
#     )


# @pytest.fixture
# def itm_call(european_option_factory):
#     return european_option_factory(
#         strike=80,
#         maturity=1.0,
#         option_type="call"
#     )


# @pytest.fixture
# def otm_call(european_option_factory):
#     return european_option_factory(
#         strike=120,
#         maturity=1.0,
#         option_type="call"
#     )


# @pytest.fixture
# def itm_put(european_option_factory):
#     return european_option_factory(
#         strike=120,
#         maturity=1.0,
#         option_type="put"
#     )


# @pytest.fixture
# def otm_put(european_option_factory):
#     return european_option_factory(
#         strike=80,
#         maturity=1.0,
#         option_type="put"
#     )

# # =========================================================
# # MODEL FACTORY
# # =========================================================

# @pytest.fixture
# def black_scholes_model_factory():
#     def make(
#         *,
#         rate=0.05,
#         sigma=0.20,
#         dividend_yield=0.00
#     ):
#         return BlackScholesModel(
#             rate,
#             sigma,
#             dividend_yield
#         )
#     return make


# @pytest.fixture
# def standard_model(black_scholes_model_factory):
#     return black_scholes_model_factory()


# @pytest.fixture
# def high_vol_model(black_scholes_model_factory):
#     return black_scholes_model_factory(sigma=0.50)


# @pytest.fixture
# def low_vol_model(black_scholes_model_factory):
#     return black_scholes_model_factory(sigma=0.10)

# # =========================================================
# # PRICER FACTORIES
# # =========================================================

# @pytest.fixture
# def black_scholes_pricer_factory(black_scholes_model_factory):
#     def make(model=None):
#         if model is None:
#             model = black_scholes_model_factory()
#         return BlackScholesPricer(model)
#     return make


# @pytest.fixture
# def standard_bs_pricer(black_scholes_pricer_factory):
#     return black_scholes_pricer_factory()

# # =========================================================
# # MARKET INPUT FIXTURES
# # =========================================================

# @pytest.fixture
# def spot():
#     return 100.0


# @pytest.fixture
# def lower_spot():
#     return 90.0


# @pytest.fixture
# def higher_spot():
#     return 110.0

# # =========================================================
# # KNOWN BENCHMARK CASES
# # =========================================================

# @pytest.fixture
# def benchmark_bs_call_case():
#     """
#     Standard textbook Black-Scholes benchmark:

#     S = 100
#     K = 100
#     r = 5%
#     sigma = 20%
#     T = 1

#     Known approximate call price:
#     10.4506
#     """
#     return {
#         "spot": 100.0,
#         "strike": 100.0,
#         "rate": 0.05,
#         "sigma": 0.20,
#         "dividend_yield": 0.00,
#         "maturity": 1.0,
#         "option_type": "call",
#         "expected_price": 10.4505835,
#     }


# # =========================================================
# # FUTURE MONTE CARLO FIXTURES
# # =========================================================

# @pytest.fixture
# def mc_small_paths():
#     return 1_000


# @pytest.fixture
# def mc_large_paths():
#     return 100_000


# @pytest.fixture
# def mc_steps():
#     return 252


# # =========================================================
# # FUTURE BINOMIAL TREE FIXTURES
# # =========================================================

# @pytest.fixture
# def tree_small_steps():
#     return 25


# @pytest.fixture
# def tree_large_steps():
#     return 1000
