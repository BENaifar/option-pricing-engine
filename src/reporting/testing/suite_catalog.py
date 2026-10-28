from src.reporting.testing.suite_description import SuiteDescription

SUITE_CATALOG: dict[str, SuiteDescription] = {
    "test_black_scholes": SuiteDescription(
        "Closed-form Black-Scholes",
        "Reference prices and analytic Greeks of the closed-form pricer.",
        "Disabled: every test is commented out (written against the old snapshot API).",
    ),
    "test_binomial_tree": SuiteDescription(
        "Binomial tree",
        "European call and put prices of the Cox-Ross-Rubinstein tree, put-call parity.",
        "Compares against known Black-Scholes values on a flat market (S=100, K=100, T=1).",
    ),
    "test_monte_carlo": SuiteDescription(
        "Monte Carlo",
        "Prices, put-call parity and price statistics for every variance reduction technique.",
        "Tolerances in standard errors (4 SE) against the closed form; antithetic and control variate must lower the standard error.",
    ),
    "test_model_agreement": SuiteDescription(
        "Cross-model agreement",
        "Monte Carlo and binomial tree agree with the closed form.",
        "Same option and market priced by each pricer: tree within 0.001, Monte Carlo within 4 standard errors.",
    ),
    "test_model_convergence": SuiteDescription(
        "Numerical convergence",
        "Errors shrink as the numerical resolution grows.",
        "Tree with 10 / 50 / 1000 steps: error must decrease. MC with 1k / 50k / 200k paths: standard error must fall like 1 / sqrt(paths).",
    ),
    "test_invariants": SuiteDescription(
        "No-arbitrage bounds",
        "Model-free price bounds for every pricer.",
        "Checks e.g. max(S e^{-qT} - K e^{-rT}, 0) <= C <= S and the put equivalents.",
    ),
    "test_american": SuiteDescription(
        "American options",
        "Early exercise on the binomial tree.",
        "American put-call inequality, American >= European, call bounds with dividends.",
    ),
    "test_extreme_regimes": SuiteDescription(
        "Extreme regimes",
        "Stability with extreme spot, rate, volatility and dividend inputs.",
        "Parametrised stress scenarios: prices stay finite, within bounds, with the right limits (e.g. sigma -> 0).",
    ),
    "test_stochastic_properties": SuiteDescription(
        "Monte Carlo randomness",
        "Reproducibility with a fixed seed and stability across runs.",
        "Same seed gives identical prices; repeated runs differ, by less than 4 standard errors.",
    ),
    "test_validation": SuiteDescription(
        "Input validation",
        "Invalid inputs are rejected with clear errors.",
        "Negative or non-integer steps / paths / seeds, wrong scheme types, invalid strikes, maturities, option types.",
    ),
    "test_market_data": SuiteDescription(
        "Market data module",
        "Loaders, curves, implied volatility, vol surface, put-call parity calibration of spot and carry.",
        "Offline: a fake provider serves a synthetic chain priced from a known smile, which the surface must recover.",
    ),
    "test_api": SuiteDescription(
        "REST API",
        "Endpoints, request validation, response mapping and error status codes.",
        "Offline: the FastAPI app with the pipeline swapped for a fake market through dependency overrides.",
    ),
    "test_reporting": SuiteDescription(
        "Report generation",
        "Market comparison, test result parsing and PDF rendering.",
        "Offline: a fake market with a 1% spread must be repriced inside its spread; the PDF renders with and without optional sections.",
    ),
    "test_live_market": SuiteDescription(
        "Live market comparison",
        "Model prices against real bid/ask quotes.",
        "Hits Yahoo Finance; run with pytest -m live. Its results are the market comparison section of this report.",
    ),
}
