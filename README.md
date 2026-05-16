# Quantitative Option Pricing Engine

![Python](https://img.shields.io/badge/python-3.11+-black?style=flat-square)
![Tests](https://img.shields.io/badge/tests-pytest-black?style=flat-square)
![Architecture](https://img.shields.io/badge/design-modular-black?style=flat-square)
![Domain](https://img.shields.io/badge/domain-quantitative_finance-black?style=flat-square)

A production-oriented quantitative finance engine focused on option pricing, numerical methods, stochastic simulation, and market modeling.

The system is built as an extensible quantitative infrastructure rather than a collection of isolated pricing scripts. Emphasis is placed on correctness, modularity, numerical robustness, and scalable architecture suitable for derivatives engineering workflows.

---

# Overview

This repository implements a modular derivatives pricing framework supporting:

- Closed-form pricing models
- Lattice methods
- Monte Carlo simulation
- Numerical Greeks (analytical + finite difference)
- Cross-model validation
- Deterministic stochastic testing infrastructure
- Market data abstraction layer (in progress)

The design follows incremental development principles with strict separation between:
- instruments
- models
- pricers
- numerical engines
- market data construction layer

---

# Key Features

## Pricing Models
- Black-Scholes analytical model
- Binomial tree model (European & American options)
- Monte Carlo simulation engine

## Instruments
- European options
- American options
- Extensible option type system

## Greeks System
- Analytical Greeks (Black-Scholes)
- Finite-difference Greeks framework
- Shared bumping infrastructure (`market_bumper.py`)
- Monte Carlo consistent random number handling

## Numerical Engine
- Euler scheme
- Exact GBM scheme
- Newton-Raphson solver
- Scheme abstraction layer

## Market Data Layer (Advanced)
- Yield curves
- Dividend curves
- Volatility curves
- Implied volatility calibration
- Market data snapshot system

## Testing & Validation
- Model agreement tests
- Convergence validation
- Arbitrage invariant enforcement
- Extreme regime robustness
- Monte Carlo stochastic stability
- Input validation suite

---

# Architecture Philosophy

The system is structured around strict separation of concerns:

- Pricing logic is isolated in pricers
- Stochastic dynamics are isolated in models and numerics
- Market data is represented as immutable snapshots
- Calibration logic is separated from runtime pricing
- Greeks computation is decoupled from pricing engines

The architecture avoids:
- monolithic market objects
- hidden dependencies between models
- coupling between calibration and pricing runtime
- premature abstraction of volatility structures

---

# Implemented Models and Methods

## Models (`src/models`)
- `black_scholes_model.py`
- `time_dependent_model.py`
- `base_model.py`

## Instruments (`src/instruments`)
- `base_option.py`
- `european_option.py`
- `american_option.py`
- `option_types.py`

## Pricers (`src/pricers`)
- `black_scholes.py`
- `binomial_tree.py`
- `monte_carlo.py`
- `base_pricer.py`

## Greeks (`src/greeks`)
- `greeks.py`
- `numerical_greeks.py`
- `finite_differences_greeks.py`
- `greeks_bumps_config.py`

## Numerics (`src/numerics`)
- `euler_scheme.py`
- `exact_gbm_scheme.py`
- `base_scheme.py`
- `newton_raphson.py`

## Market Data (`src/market_data`)
### Core
- `market_data_snapshot.py`
- `market_data_dto.py`
- `market_bumper.py`
- `implied_vol_inversion_functs.py`

### Services
- `services/market_data_service.py`

### Providers
- `static_market_data_provider.py`
- `csv_market_data_provider.py`
- `yahoo_market_data_provider.py`
- `base_market_data_provider.py`

### Curves
- `yield_curve.py`
- `dividend_curve.py`
- `volatility_curve.py`

### Calibrators
- `calibrators/implied_volatility.py`

## Time Utilities
- `to_years.py`
- `str_to_date.py`

---

# Repository Structure

```text
src/
│
├── core/
│   └── config.py
│
├── instruments/
│   ├── base_option.py
│   ├── european_option.py
│   ├── american_option.py
│   └── option_types.py
│
├── models/
│   ├── base_model.py
│   ├── black_scholes_model.py
│   └── time_dependent_model.py
│
├── pricers/
│   ├── base_pricer.py
│   ├── black_scholes.py
│   ├── binomial_tree.py
│   └── monte_carlo.py
│
├── greeks/
│   ├── greeks.py
│   ├── numerical_greeks.py
│   ├── finite_differences_greeks.py
│   └── greeks_bumps_config.py
│
├── numerics/
│   ├── base_scheme.py
│   ├── euler_scheme.py
│   ├── exact_gbm_scheme.py
│   └── newton_raphson.py
│
├── market_data/
│   ├── providers/
│   ├── services/
│   ├── curves/
│   ├── calibrators/
│   ├── market_data_snapshot.py
│   ├── market_data_dto.py
│   ├── market_bumper.py
│   └── implied_vol_inversion_functs.py
│
├── simulations/
│   └── simulation_result.py
│
├── time/
│   ├── to_years.py
│   └── str_to_date.py
│
└── tests/
    ├── conftest.py
    ├── scenario.py
    ├── test_black_scholes.py
    ├── test_binomial_tree.py
    ├── test_monte_carlo.py
    ├── test_american.py
    ├── test_model_agreement.py
    ├── test_model_convergence.py
    ├── test_extreme_regimes.py
    ├── test_invariants.py
    ├── test_stochastic_properties.py
    └── test_validation.py
```

---

# Installation

```bash
git clone https://github.com/yourusername/quant-option-pricing-engine.git
cd quant-option-pricing-engine
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

# Example Usage

## Black-Scholes Pricing

```python
from src.instruments.european_option import EuropeanOption
from src.pricers.black_scholes import BlackScholesPricer
from src.market_data.market_data_snapshot import MarketDataSnapshot

option = EuropeanOption(strike=100, maturity=1.0, option_type="call")

market = MarketDataSnapshot(
    spot=100,
    rate=0.05,
    volatility=0.20,
    dividend_yield=0.0
)

pricer = BlackScholesPricer()

price = pricer.price(option, market)
greeks = pricer.greeks(option, market)
```

---

# Testing

Run full validation suite:

```bash
pytest
```

Test coverage includes:

- Pricing correctness
- Model agreement
- Numerical convergence
- Arbitrage invariants
- Extreme regime stability
- Monte Carlo stability
- Input validation

---

# Performance Philosophy

Performance is explicitly deferred until:

- numerical correctness is validated
- model interfaces stabilize
- market data layer is completed

Current focus:
- deterministic correctness
- numerical stability
- architectural clarity

Future optimization:
- vectorization
- parallel simulation
- caching strategies
- low-level acceleration

---

# Market Data Layer (In Progress)

The Market Data Layer introduces structured financial data representation:

## Providers
- CSV-based providers
- Static providers
- Yahoo Finance integration
- Extensible provider interface

## Curves
- Yield curves
- Dividend curves
- Volatility curves

## Calibration
- Implied volatility extraction
- Numerical inversion routines
- Surface construction pipelines

## Snapshot System
Immutable market snapshots combining:
- spot data
- curves
- volatility structures

used as the single input to pricing engines.

---

# Design Principles

- Explicit dependency injection
- Separation of construction and runtime logic
- Immutable market snapshots
- Interface-driven design
- Deterministic numerical behavior
- Incremental complexity growth
- No hidden coupling between modules

---

# Why This Project Exists

This project exists to implement a production-grade quantitative finance engine built from first principles.

It avoids:
- toy-level pricing scripts
- tightly coupled quant frameworks
- non-deterministic numerical behavior
- unclear separation between calibration and pricing

The goal is to build a system that mirrors real quantitative infrastructure design used in derivatives pricing environments.

---

# Future Roadmap

## Phase 3 — Market Data Layer
- Full curve infrastructure
- Volatility modeling expansion
- Calibration pipelines
- Snapshot standardization

## Phase 4 — Performance Layer
- Vectorized pricing
- Parallel Monte Carlo
- Memory optimization

## Phase 5 — Testing Expansion
- Statistical validation layer
- Regression hardening
- CI automation

## Phase 6 — Documentation
- Mathematical derivations
- Model assumptions
- Architecture diagrams

## Phase 7 — Visualization & Interface
- Surface visualization
- Scenario analysis tools
- API layer

---

# License

MIT
