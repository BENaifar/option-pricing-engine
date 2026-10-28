# Commit plan

The worktree contains several independent changes, and the current branch is `main`. Before committing, create a feature branch with `git switch -c feat/market-data-pricing-api-reporting`. Then run these PowerShell commands from the repository root, in order, and review each staged diff before committing. Each block stages only the paths for that commit. These commands are a plan only; they have not been run.

## 1. Runtime dependencies

```powershell
git add -A -- requirements.txt
git commit -m "chore(deps): add API and report runtime dependencies" -m "Why: the new HTTP service, PDF renderer, and benchmark tooling require declared runtime packages."
```

## 2. Market-data calibration and snapshot changes

```powershell
git add -A -- src\core\config.py src\core\exceptions.py src\market_data\calibrators\volatility_smile_builder.py src\market_data\calibrators\implied_spot.py src\market_data\curves\dividend_curve.py src\market_data\curves\volatility_smile_curve.py src\market_data\curves\yield_curve.py src\market_data\loaders\dividend_loader.py src\market_data\loaders\rates_loader.py src\market_data\loaders\spot_loader.py src\market_data\loaders\volatilityLoader.py src\market_data\market_data_snapshot.py src\market_data\models\option_quote.py src\market_data\models\rate.py src\market_data\models\volatility_surface.py src\market_data\models\flat_volatility.py src\market_data\providers\yahoo_market_data_provider.py src\market_data\services\market_data_service.py src\market_data\static_market_data_snapshot.py tests\test_market_data_service.py tests\test_market_data.py tests\fake_market_data_provider.py
git commit -m "feat(market-data): calibrate snapshots from option-chain quotes" -m "Why: parity-derived spot and carry, validated quote inputs, and term structures make pricing inputs consistent with the observed market."
```

## 3. Dividend-aware pricing and scheme organization

```powershell
git add -A -- src\models\black_scholes_model.py src\pricers\binomial_tree.py src\pricers\closed_black_scholes.py src\process\base_process.py src\process\gbm_process.py src\schemes\base_scheme.py src\schemes\exact_gbm_scheme.py src\numerics\exact_gbm_scheme.py tests\conftest.py tests\scenario.py tests\test_american.py tests\test_binomial_tree.py tests\test_black_scholes.py tests\test_extreme_regimes.py tests\test_invariants.py tests\test_model_agreement.py tests\test_model_convergence.py tests\test_validation.py
git commit -m "fix(pricing): apply dividend carry consistently across pricers" -m "Why: using the same risk-neutral rates, dividends, volatility, and process inputs prevents model disagreement and preserves pricing invariants."
```

## 4. Monte Carlo variance reduction and uncertainty estimates

```powershell
git add -A -- src\pricers\monte_carlo.py src\pricers\monte_carlo_price_statistics.py tests\test_monte_carlo.py tests\test_stochastic_properties.py
git commit -m "feat(monte-carlo): add variance reduction and price statistics" -m "Why: uncertainty estimates and optional variance reduction make simulation results more informative and reproducible."
```

## 5. Reusable pricing pipeline

```powershell
git add -A -- src\pipeline tests\fake_pipeline.py src\greeks\bump_and_reprice_greeks.py src\process\process_factory.py
git commit -m "feat(pipeline): compose cached market data and pricing workflows" -m "Why: a shared pipeline centralizes snapshot caching, pricer selection, and Greeks calculation for application clients."
```

## 6. Reporting and PDF generation

```powershell
git add -A -- src\reporting tests\test_reporting.py reports\AAPL_call_350_report.pdf
git commit -m "feat(reporting): generate market-aware option reports" -m "Why: structured market comparisons, accuracy studies, warnings, and rendered PDF reports make pricing results auditable."
```

## 7. HTTP API

```powershell
git add -A -- src\api tests\test_api.py
git commit -m "feat(api): expose pricing, market data, and reports over HTTP" -m "Why: typed request and response schemas provide a stable interface to the pricing and reporting workflows."
```

## 8. Command-line entry point

```powershell
git add -A -- main.py
git commit -m "feat(cli): add pricing, market-data, report, and serve commands" -m "Why: users need one entry point for local pricing workflows and launching the HTTP service."
```

## 9. Benchmark tools and recorded results

```powershell
git add -A -- scripts\live_benchmark.py scripts\numerics_benchmark.py scripts\parity_ablation.py docs\benchmarks.md docs\img\model_vs_market_aapl.png
git commit -m "perf(benchmarks): add reproducible pricing studies" -m "Why: repeatable numerical and live-market measurements document model behavior and expose calibration tradeoffs."
```

## 10. Project and numerical-method documentation

```powershell
git add -A -- README.md docs\models_and_numerics.md
git commit -m "docs(engine): explain the pricing architecture and measured behavior" -m "Why: updated usage, architecture, and numerical-method guidance helps users reproduce and interpret results."
```

## 11. Opt-in live-market integration tests

```powershell
git add -A -- pytest.ini tests\test_live_market.py
git commit -m "test(market-data): add opt-in live quote validation" -m "Why: live-feed checks should validate calibration behavior without making the offline test suite depend on network access or market hours."
```

## 12. This commit plan

```powershell
git add -A -- COMMIT_PLAN.md
git commit -m "docs(git): document focused commit commands" -m "Why: explicit staging groups and rationale keep the changes reviewable and avoid a single mixed-purpose commit."
```

## Review notes

- The pricing commit follows the market-data commit because it consumes the curve-backed snapshot types introduced there.
- Reporting precedes the API commit because the API application exposes report endpoints.
- The PDF and chart are generated artifacts included with their corresponding reporting/benchmark changes; omit them from their commands if they are not intended to be versioned.
- The requested `src\api\schemas.py` is included in the API commit.
