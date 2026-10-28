# Benchmarks

All runs: 2026-10-28, about 17:00–17:10 local time (US market open), Windows 11, Python 3.12.10.
Rates came from FRED files ending 2026-05-04. Run every command from the project root.

## Model vs live market

Command: `python -m scripts.live_benchmark TICKER [plot.png]`

- **Quote filter** (`LiquidityFilter`): T from 30 to 365 days, K/S from 0.85 to 1.15, relative spread ≤ 10%.
- **Hit:** model price within [bid − 0.01, ask + 0.01].
- **Pricers:** ITM puts use a 500-step American tree; every other quote uses the European closed form.

| Ticker | Spot (quoted → parity) | Smiles | Snapshot time |
|---|---|---:|---:|
| AAPL | 345.3600 → 345.2628 | 18 | 8.0 s |
| MSFT | 527.6400 → 527.5870 | 19 | 7.0 s |

| Ticker | Set | n | Hit | MAE | Median \|e\|/mid | p90 \|e\|/mid | Mean signed | Median spread/mid |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AAPL | in-sample OTM | 125 | 100.0% | 6.1e-10 | 9e-14 | 2.6e-10 | 5e-10 | 2.20% |
| AAPL | out-of-sample ITM | 131 | 79.4% | 0.308 | 0.61% | 1.91% | +0.048 | 2.40% |
| AAPL | ITM calls | 69 | 94.2% | 0.240 | 0.58% | 0.92% | −0.207 | 2.03% |
| AAPL | ITM puts (tree) | 62 | 62.9% | 0.383 | 0.83% | 2.46% | +0.331 | 2.97% |
| MSFT | in-sample OTM | 223 | 100.0% | 0.0048 | 3e-14 | 2.1e-10 | 0.0012 | 2.87% |
| MSFT | out-of-sample ITM | 209 | 71.3% | 0.593 | 0.79% | 1.96% | +0.135 | 2.22% |
| MSFT | ITM calls | 111 | 90.1% | 0.435 | 0.65% | 1.07% | −0.375 | 2.20% |
| MSFT | ITM puts (tree) | 98 | 50.0% | 0.772 | 1.35% | 2.48% | +0.712 | 2.23% |

The in-sample errors are close to zero by construction, because the spline interpolates every calibration quote.

## Parity calibration on vs off

Command: `python -m scripts.parity_ablation TICKER`. This run is a separate snapshot, so its numbers differ from the table above.

| Ticker | Parity | Spot | Out-of-sample n | Hit | MAE | Median \|e\|/mid |
|---|---|---:|---:|---:|---:|---:|
| AAPL | off | 345.4300 | 131 | 46.6% | 0.788 | 1.42% |
| AAPL | on | 345.1887 | 131 | 74.0% | 0.336 | 0.71% |
| MSFT | off | 527.7000 | 209 | 24.4% | 1.491 | 1.76% |
| MSFT | on | 527.4782 | 209 | 67.5% | 0.589 | 0.65% |

## Live test suite

| Command | Result |
|---|---|
| `pytest -m live -s` | AAPL: 4 passed; calibration 100.0%, out-of-sample 70.2% |
| `LIVE_TICKER=MSFT pytest -m live -s` | MSFT: 3 passed, 1 failed (`test_out_of_sample_itm_quotes`, below the 70% threshold) |

## Offline numerics

Command: `python -m scripts.numerics_benchmark`. The tables are in [models_and_numerics.md](models_and_numerics.md) (tree convergence, Monte Carlo SE by technique, Euler bias).

American put on the tree (same parameters, 500 / 1000 / 2000 steps): 6.65882 / 6.65976 / 6.66023. The European closed form is 6.33008.

## Offline suite

`pytest`: 184 passed, 4 deselected (live), 46 s.

| File | Tests | File | Tests |
|---|---:|---|---:|
| test_market_data | 52 | test_validation | 12 |
| test_api | 27 | test_american | 5 |
| test_invariants | 24 | test_binomial_tree | 3 |
| test_monte_carlo | 20 | test_model_agreement | 2 |
| test_reporting | 19 | test_model_convergence | 2 |
| test_extreme_regimes | 16 | test_stochastic_properties | 2 |
