# Models and numerics

Each section points to the code it describes.

## 1. Black-Scholes dynamics

The underlying follows a geometric Brownian motion under the risk-neutral measure ([gbm_process.py](../src/process/gbm_process.py)):

$$
dS_t = (r - q)\,S_t\,dt + \sigma\,S_t\,dW_t
$$

`BlackScholesModel` ([black_scholes_model.py](../src/models/black_scholes_model.py)) reads **one constant value per option** from the snapshot curves:

$$
r = r(T), \qquad q = q(T), \qquad \sigma = \sigma(K, T)
$$

The process is therefore a flat-parameter GBM for each option. `TimeDependentModel` exists in `src/models/`, but the pipeline does not use it.

## 2. Closed form

[closed_black_scholes.py](../src/pricers/closed_black_scholes.py):

$$
d_1 = \frac{\ln(S/K) + (r - q + \tfrac12\sigma^2)T}{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}
$$

$$
C = S e^{-qT} N(d_1) - K e^{-rT} N(d_2), \qquad P = K e^{-rT} N(-d_2) - S e^{-qT} N(-d_1)
$$

## 3. Binomial tree (Cox-Ross-Rubinstein)

[binomial_tree_scheme.py](../src/schemes/binomial_tree_scheme.py) and [binomial_tree.py](../src/pricers/binomial_tree.py):

$$
u = e^{\sigma\sqrt{\Delta t}}, \quad d = 1/u, \quad p = \frac{e^{(r-q)\Delta t} - d}{u - d}
$$

Backward induction discounts with $e^{-r\Delta t}$. For American options, each node takes $\max(\text{intrinsic}, \text{continuation})$.

Convergence is first order, and the error oscillates between odd and even step counts. Measured with `python -m scripts.numerics_benchmark` (S = K = 100, T = 1, r = 5%, q = 2%, σ = 20%, reference 9.227006):

| steps | error | time |
|---:|---:|---:|
| 50 | −3.88e-02 | 0.001 s |
| 100 | −1.94e-02 | 0.001 s |
| 101 | +1.83e-02 | 0.001 s |
| 200 | −9.71e-03 | 0.003 s |
| 500 | −3.89e-03 | 0.011 s |
| 1000 | −1.94e-03 | 0.034 s |
| 2000 | −9.72e-04 | 0.123 s |

The error is about −1.94/N for even N. The tree is a dense `(N+1) × (N+1)` array, so memory grows as O(N²). No Richardson extrapolation or smoothing is applied.

## 4. Monte Carlo

[monte_carlo.py](../src/pricers/monte_carlo.py). Time is split into `n_steps` equal steps, with $\Delta W = Z\sqrt{\Delta t}$ and $Z \sim N(0,1)$ drawn from `numpy.random.default_rng(seed)`.

**Exact scheme** ([exact_gbm_scheme.py](../src/schemes/exact_gbm_scheme.py)):

$$
S_{t+\Delta t} = S_t \exp\!\big((r - q - \tfrac12\sigma^2)\Delta t + \sigma\,\Delta W\big)
$$

**Euler scheme** ([euler_scheme.py](../src/schemes/euler_scheme.py)):

$$
S_{t+\Delta t} = S_t + (r-q)S_t\,\Delta t + \sigma S_t\,\Delta W
$$

Only the terminal value is used, so under flat parameters the exact scheme has no discretisation bias for any `n_steps`. Euler bias from the same benchmark (200 000 paths, no variance reduction):

| n_steps | error | standard error |
|---:|---:|---:|
| 1 | −0.1272 | 0.0270 |
| 4 | −0.0240 | 0.0299 |
| 16 | −0.0205 | 0.0305 |
| 64 | −0.0292 | 0.0309 |

At 1 step the bias is about 4.7 standard errors. From 4 steps on, it cannot be resolved at this path count.

### Estimator and statistics

Every path gives one observation $Y_i$. [monte_carlo_price_statistics.py](../src/pricers/monte_carlo_price_statistics.py) reports:

$$
\hat V = \bar Y, \quad s^2 = \frac{1}{n-1}\sum (Y_i - \bar Y)^2, \quad \text{SE} = s/\sqrt{n}, \quad \text{CI} = \hat V \pm t_{n-1,\,(1+c)/2}\,\text{SE}
$$

`one_sample_t_test(reference)` tests $H_0: E[Y] = \text{reference}$ with $t = (\hat V - \text{ref})/\text{SE}$ and $n-1$ degrees of freedom.

### Variance reduction

| Technique | Observation $Y_i$ | Paths simulated |
|---|---|---|
| `none` | $e^{-rT}\,\text{payoff}(S_T(Z_i))$ | n |
| `antithetic` | $\tfrac12\big[Y(Z_i) + Y(-Z_i)\big]$ | 2n |
| `control_variate` | $Y_i - \hat\beta\,(e^{-rT}S_T^{(i)} - S_0 e^{-qT})$, with $\hat\beta = \widehat{\text{Cov}}(Y, C)/\widehat{\text{Var}}(C)$ | n |

The control is the discounted terminal stock price, whose expectation $S_0e^{-qT}$ is known exactly. $\hat\beta$ is estimated on the same paths, which adds a bias of order 1/n. The control variate is rejected for any process other than `GBMProcess`.

Measured on the reference call (exact scheme, 1 step, seed 42):

| technique | paths | error | SE | \|error\| / SE |
|---|---:|---:|---:|---:|
| none | 10 000 | −0.0984 | 0.1388 | 0.71 |
| none | 100 000 | −0.0254 | 0.0440 | 0.58 |
| antithetic | 10 000 | +0.0255 | 0.0742 | 0.34 |
| antithetic | 100 000 | +0.0236 | 0.0232 | 1.02 |
| control_variate | 10 000 | +0.0134 | 0.0577 | 0.23 |
| control_variate | 100 000 | +0.0175 | 0.0181 | 0.97 |

With the pipeline defaults (100 000 paths, 64 steps), the SE is 0.0439 / 0.0231 / 0.0180 and the runtime 0.18 s / 0.27 s / 0.18 s for none / antithetic / control variate. Antithetic simulates twice the paths. At equal simulation cost, plain Monte Carlo with 200 000 paths would have an SE of about 0.0439/√2 ≈ 0.031, so antithetic still has the lower SE per simulated path here.

### Defaults

`MonteCarloPricer` used on its own defaults to `antithetic`. The pipeline, CLI and API default to `none` (`PricingSettings`).

## 5. Greeks

[bump_and_reprice_greeks.py](../src/greeks/bump_and_reprice_greeks.py) uses central differences for every pricer, with bump sizes from `config.ini`:

| Greek | Formula | Bump |
|---|---|---|
| delta | $(V(S+h) - V(S-h))/2h$ | $h = 0.02\,S$ |
| gamma | $(V(S+h) - 2V(S) + V(S-h))/h^2$ | $h = 0.02\,S$ |
| vega | $(V(\sigma+\epsilon) - V(\sigma-\epsilon))/2\epsilon$ | $\epsilon = 0.005$ |
| rho | $(V(r+\delta) - V(r-\delta))/2\delta$ | $\delta = 10^{-4}$ |
| theta | $-(V(T+\tau) - V(T-\tau))/2\tau$ | $\tau = 1/365$ |

- **What is bumped:** the process parameters (σ, r), not the curves. Bumping the spot does not re-read σ from the surface (sticky strike). q is never bumped.
- **Units:** vega and rho are per unit (1.00 = 100 vol points or 100% rate), and theta is per year.
- **Monte Carlo:** every bump reuses one draw of `Z` (common random numbers).
- **Tree:** the 2% spot bump moves the node lattice, so tree gamma carries lattice noise. No smoothing is applied.

## 6. Market data calibration

### Rates

FRED constant-maturity Treasury yields (DGS1M … DGS30) are read from local CSV files ([rates_loader.py](../src/market_data/loaders/rates_loader.py)), taking the last value on or before the valuation date. The quoted yields are used **directly as continuously compounded zero rates**, with no bond-equivalent conversion and no bootstrapping. [yield_curve.py](../src/market_data/curves/yield_curve.py) interpolates with PCHIP and extrapolates flat.

### Spot from put-call parity

[implied_spot.py](../src/market_data/calibrators/implied_spot.py):

$$
S = (C - P + K e^{-rT})\,e^{qT}
$$

The spot is the median over call/put pairs that meet all of these conditions:

- both legs priced from a bid/ask mid;
- |K/S − 1| ≤ 5%;
- 7 to 45 days to expiry;
- at least 3 pairs.

The parity spot is rejected if it is more than 2% from the quoted spot. q depends on S through the trailing dividend yield, so the calculation iterates S → q → S up to 5 times ([market_data_service.py](../src/market_data/services/market_data_service.py)).

### Carry curve from parity forwards

$$
F(T) = (C - P)\,e^{r(T)T} + K, \qquad q(T) = r(T) - \frac{\ln(F(T)/S)}{T}
$$

The median forward per expiry uses expiries from 30 days to 3 years, with at least 2 pairs. A carry more than 5 percentage points from the trailing dividend yield is discarded. The resulting q(T) is PCHIP-interpolated and flat outside its range. Because q(T) is fitted to the option forwards, it absorbs any error in r(T), discrete dividends and borrow cost.

### Implied volatility

- **Solver:** Newton-Raphson on the Black-Scholes price, starting from σ₀ = 0.2, with tolerance 1e-8 on price, at most 100 iterations and σ floored at 1e-4 ([implied_volatility.py](../src/market_data/calibrators/implied_volatility.py)).
- **Quotes used:** out-of-the-money only, K within 70–130% of spot, T ≥ 7 days ([volatilityLoader.py](../src/market_data/loaders/volatilityLoader.py)).
- **Rejected:** quotes that fail to converge, and vols outside (1%, 300%).
- **European formula only:** listed US equity options are American, so this is a modelling approximation.

### Volatility surface

| Dimension | Method |
|---|---|
| Strike, within one expiry | Natural cubic spline of IV in $k = \ln(K/F(T))$ through every quote, with at least 4 quotes per expiry ([volatility_smile_builder.py](../src/market_data/calibrators/volatility_smile_builder.py)). It interpolates exactly: no smoothing, no fit residual. |
| Strike, outside the quotes | k is clipped to the quoted range (flat extrapolation). |
| Maturity | Linear in total variance $w = \sigma^2 T$ between neighbouring expiries; flat outside ([volatility_surface.py](../src/market_data/models/volatility_surface.py)). |

The surface has no checks for butterfly arbitrage (convexity in K) or calendar arbitrage (w increasing in T).

## 7. GARCH

**Not implemented.** The repository contains no GARCH, historical or realised volatility model. Volatility comes only from option-implied quotes. See the roadmap in the README.
