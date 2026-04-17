# European Options Pricing Engine - Documentation

## 1. High-Level Overview

- **Purpose:** A lightweight option-pricing engine implementing classical pricing methods: Black–Scholes closed-form, Monte Carlo simulation, and a binomial tree supporting American early exercise.
- **Main features:**
  - Closed-form Black–Scholes pricing for European options.
  - Monte Carlo simulation with pluggable discretization schemes (`EulerScheme`, `ExactGBMScheme`).
  - Binomial tree pricer with American/European support.
  - CLI (`engine.py`) to wire option, model, scheme and pricer choices.
- **Technology stack:** Python, NumPy, SciPy, dataclasses, argparse, pytest.
- **Architecture (text diagram):**

```
engine.py (CLI)
  ├─ constructs Option <- src/instruments/
  ├─ constructs Model  <- src/models/
  ├─ constructs Scheme <- src/schemes/ (optional)
  └─ constructs Pricer <- src/pricers/
        └─ computes price -> prints result
```

## 2. Module-Level Documentation

- `engine.py`
  - Role: CLI entrypoint, argument validation, factories (`build_option`, `build_scheme`, `build_pricer`) and `main()` orchestrator.
  - Key functions: `validate_arguments`, `build_option`, `build_scheme`, `build_pricer`, `main`.

- `src/instruments/base_option.py`
  - Role: Base dataclass for options, validation and payoff computation.
  - Key class: `BaseOption(strike, maturity, option_type)`.

- `src/instruments/european_option.py`
  - Role: `EuropeanOption` (concrete).

- `src/instruments/american_option.py`
  - Role: `AmericanOption` (concrete, supports early exercise).

- `src/models/base_model.py`
  - Role: Abstract model interface: `drift(S,t)` and `diffusion(S,t)`.

- `src/models/black_scholes_model.py`
  - Role: `BlackScholesModel` implementing GBM drift/diffusion.

- `src/schemes/base_scheme.py`
  - Role: Abstract scheme interface `step(model, S, t, dt, brownian_increment)`.

- `src/schemes/euler_scheme.py`
  - Role: `EulerScheme` (Euler–Maruyama update).

- `src/schemes/exact_gbm_scheme.py`
  - Role: `ExactGBMScheme` (analytic GBM step).

- `src/pricers/black_scholes.py`
  - Role: Closed-form Black–Scholes pricing for European options (`BlackScholesPricer`).

- `src/pricers/monte_carlo.py`
  - Role: `MonteCarloPricer` with `simulate()` and `price()` using a `BaseScheme`.

- `src/pricers/binomial_tree.py`
  - Role: `BinomialTree` CF-RR style pricing supporting American early exercise.

- `src/market_data/market_data.py`
  - Role: Simple dataclass holder for market parameters with basic validation.

## 3. Function / Class Documentation (selected)

- `BaseOption` (`src/instruments/base_option.py`)
  - Parameters:
    - `strike: float` — strike price (must be > 0).
    - `maturity: float` — time to expiry in years (must be > 0).
    - `option_type: str` — `'call'` or `'put'` (default `'call'`).
  - Methods:
    - `payoff(ST)` -> payoff at terminal price(s) (scalar or ndarray).
    - `is_american()` -> abstract boolean.
  - Side effects: validation raises `ValueError` for invalid inputs.
  - Example:

```python
from src.instruments.european_option import EuropeanOption
opt = EuropeanOption(strike=100.0, maturity=1.0, option_type="call")
print(opt.payoff(110.0))  # -> 10.0
```

- `BlackScholesModel` (`src/models/black_scholes_model.py`)
  - Parameters: `rate: float`, `sigma: float`, `dividend_yield: float = 0.0`.
  - Methods: `drift(S,t)`, `diffusion(S,t)`.
  - Side effects: `sigma` validated positive.

- `BlackScholesPricer` (`src/pricers/black_scholes.py`)
  - Methods: `price(option, spot)` returns Black–Scholes price (float).
  - Side effects: none.

- `MonteCarloPricer` (`src/pricers/monte_carlo.py`)
  - Parameters: `model: BaseModel`, `scheme: BaseScheme`, `paths: int`, `seed: int`.
  - Methods: `simulate(option, spot, n_steps=1000)` returns array of paths; `price(option, spot, n_steps=1000)` returns discounted average payoff.
  - Side effects: uses NumPy RNG; `__post_init__` validates `paths` and `seed`.

- `BinomialTree` (`src/pricers/binomial_tree.py`)
  - Parameters: `spot`, `r`, `sigma`, `q`, `steps`.
  - Methods: `price(option)` chooses American/European backward induction.
  - Side effects: input validation in `__post_init__`.

## 4. Data Structures & Models

- `BaseOption` — canonical contract: `strike`, `maturity`, `option_type`.
- `BaseModel` — SDE coefficients used by schemes/pricers.
- `BaseScheme` — discretization behavior; `EulerScheme` and `ExactGBMScheme` are concrete.
- `MonteCarloPricer` composes `BaseModel` + `BaseScheme` + RNG.
- `BinomialTree` uses market parameters directly and the `Option` to compute payoffs.

## 5. Execution Flow

1. Run `engine.py` (script) with CLI args: `spot rate sigma dividend option model scheme pricer [--strike --maturity ...]`.
2. `validate_arguments()` enforces compatibility rules.
3. `build_option()` returns `EuropeanOption` or `AmericanOption`.
4. `BlackScholesModel` is instantiated from CLI market parameters.
5. `build_scheme()` instantiates `EulerScheme` or `ExactGBMScheme` (or `None` for closed_form).
6. `build_pricer()` returns a concrete pricer instance.
7. Price computation: `BinomialTree.price(option)` or `pricer.price(option, spot)` for other pricers.
8. Result printed; script returns exit code `0` on success or `1` on `ValueError`/`TypeError`.

## 6. Configuration & Environment

- No environment variables are required.
- Dependencies: `numpy`, `scipy`, `pytest`.
- Install (example):

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Files in repo that affect configuration: `engine.py` (CLI arguments).

## 7. Error Handling & Edge Cases

- Input validation is implemented in dataclass `__post_init__` methods across models/pricers/options and in `engine.validate_arguments()`.
- Known limitations:
  - `BlackScholesPricer` only supports European options.
  - `MonteCarloPricer` does simple terminal payoff sampling and discounting (no variance reduction or path-dependent/early-exercise logic).
  - `time_dependent_model.py` is a placeholder.
  - `MarketData` requires strictly positive dividend yield in current implementation; consider allowing zero.

## 8. Contribution Guide

- Adding a pricer:
  1. Implement a pricer class in `src/pricers/` with a `price(...)` method.
  2. Add CLI choice in `engine.py` and wire `build_pricer()`.
  3. Add unit tests under `tests/unit/`.

- Adding a scheme:
  1. Subclass `BaseScheme` in `src/schemes/` and implement `step()`.
  2. Wire into `engine.build_scheme()` and add tests.

- Style guidelines:
  - Use `dataclasses` for simple containers.
  - Keep computational functions pure (IO in `engine.py`).
  - Prefer NumPy vectorized operations for performance.

## Examples

- CLI example (Black–Scholes closed-form):

```bash
python engine.py 100 0.01 0.2 0.0 european black_scholes closed_form black_scholes --strike 100 --maturity 1.0
```

- Programmatic example:

```python
from src.instruments.european_option import EuropeanOption
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.black_scholes import BlackScholesPricer

opt = EuropeanOption(strike=100.0, maturity=1.0)
model = BlackScholesModel(rate=0.01, sigma=0.2)
pricer = BlackScholesPricer(model)
price = pricer.price(opt, spot=100.0)
print(price)
```

## Suggested immediate improvements

- Add `requirements.txt` (provided) and pin versions.
- Allow zero dividend yield in `MarketData` validation.
- Add unit tests ensuring Monte Carlo convergence against Black–Scholes for simple cases.
