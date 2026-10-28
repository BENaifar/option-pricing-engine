import time

from src.instruments.american_option import AmericanOption
from src.instruments.european_option import EuropeanOption
from src.instruments.option_types import OptionType
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.models.flat_volatility import FlatVolatility
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.binomial_tree import BinomialTree
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer, VarianceReductionTechnique
from src.process.process_factory import ProcessFactory
from src.schemes.binomial_tree_scheme import BinomialTreeScheme
from src.schemes.euler_scheme import EulerScheme
from src.schemes.exact_gbm_scheme import ExactGBMScheme

S, K, T = 100.0, 100.0, 1.0
market = MarketDataSnapshot(ticker="TEST", spot=S, rate=YieldCurve(0.05), sigma=FlatVolatility(0.20),
                            dividend_yield=DividendCurve(None, None, 0.02))
process = ProcessFactory.create(BlackScholesModel(market, strike=K, maturity=T))
call = EuropeanOption(strike=K, maturity=T, option_type=OptionType.CALL)
reference = ClosedBlackScholesPricer().price(call, process, S)
print(f"reference call S=K=100 T=1 r=5% q=2% sigma=20%: {reference:.6f}")

print("\n# binomial tree, European call")
for steps in (50, 100, 101, 200, 500, 1000, 2000):
    start = time.perf_counter()
    price = BinomialTree(scheme=BinomialTreeScheme(), steps=steps).price(call, process, S)
    print(f"steps={steps:5d} error={price - reference:+.2e} time={time.perf_counter() - start:.3f}s")

print("\n# American put, tree")
put_am = AmericanOption(strike=K, maturity=T, option_type=OptionType.PUT)
put_eu = EuropeanOption(strike=K, maturity=T, option_type=OptionType.PUT)
for steps in (500, 1000, 2000):
    am = BinomialTree(scheme=BinomialTreeScheme(), steps=steps).price(put_am, process, S)
    print(f"steps={steps} american={am:.5f} european_closed={ClosedBlackScholesPricer().price(put_eu, process, S):.5f}")

print("\n# Monte Carlo exact scheme, n_steps=1")
for technique in VarianceReductionTechnique:
    for paths in (10_000, 100_000):
        pricer = MonteCarloPricer(scheme=ExactGBMScheme(), paths=paths, n_steps=1, seed=42, variance_reduction_technique=technique)
        start = time.perf_counter()
        stats = pricer.price_with_statistics(call, process, S)
        elapsed = time.perf_counter() - start
        print(f"{technique.value:16s} paths={paths:7d} error={stats.price - reference:+.4f} se={stats.standard_error:.4f} "
              f"|err|/se={abs(stats.price - reference) / stats.standard_error:.2f} time={elapsed:.3f}s")

print("\n# Monte Carlo default pipeline settings (100k paths, 64 steps)")
for technique in VarianceReductionTechnique:
    pricer = MonteCarloPricer(scheme=ExactGBMScheme(), paths=100_000, n_steps=64, seed=42, variance_reduction_technique=technique)
    start = time.perf_counter()
    stats = pricer.price_with_statistics(call, process, S)
    print(f"{technique.value:16s} se={stats.standard_error:.4f} time={time.perf_counter() - start:.2f}s")

print("\n# Euler bias vs steps (200k paths, no VR)")
for n_steps in (1, 4, 16, 64):
    pricer = MonteCarloPricer(scheme=EulerScheme(), paths=200_000, n_steps=n_steps, seed=7, variance_reduction_technique="none")
    stats = pricer.price_with_statistics(call, process, S)
    print(f"n_steps={n_steps:3d} error={stats.price - reference:+.4f} se={stats.standard_error:.4f}")
