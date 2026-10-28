from dataclasses import dataclass

import numpy as np
from scipy.stats import t


@dataclass(frozen=True)
class MonteCarloPriceStatistics:
    price: float
    variance: float
    standard_deviation: float
    standard_error: float
    confidence_interval: tuple[float, float]
    observations: int

    def one_sample_t_test(
        self,
        reference_price: float,
        alpha: float = 0.05,
    ) -> dict[str, float | bool]:
        """Test H0: the expected simulated price equals reference_price."""
        if not np.isfinite(reference_price):
            raise ValueError("reference_price must be finite")
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")
        if self.observations < 2:
            raise ValueError("At least two observations are required")

        if self.standard_error == 0:
            if self.price == reference_price:
                statistic, p_value = 0.0, 1.0
            else:
                statistic, p_value = float("inf"), 0.0
        else:
            statistic = (
                self.price - reference_price
            ) / self.standard_error

            p_value = float(
                2 * t.sf(abs(statistic), df=self.observations - 1)
            )

        return {
            "reference_price": float(reference_price),
            "t_statistic": float(statistic),
            "p_value": float(p_value),
            "alpha": float(alpha),
            "reject_null": bool(p_value < alpha),
        }


def calculate_price_statistics(
    observations: np.ndarray,
    confidence_level: float = 0.95,
) -> MonteCarloPriceStatistics:
    """Calculate statistics from independent price-estimator observations."""
    values = np.asarray(observations, dtype=float).reshape(-1)

    if values.size < 2:
        raise ValueError("At least two observations are required")
    if not np.all(np.isfinite(values)):
        raise ValueError("Observations must all be finite")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")

    n = values.size
    price = float(np.mean(values))
    variance = float(np.var(values, ddof=1))
    standard_deviation = float(np.sqrt(variance))
    standard_error = standard_deviation / np.sqrt(n)

    critical_value = float(
        t.ppf((1 + confidence_level) / 2, df=n - 1)
    )

    interval = (
        price - critical_value * standard_error,
        price + critical_value * standard_error,
    )

    return MonteCarloPriceStatistics(
        price=price,
        variance=variance,
        standard_deviation=standard_deviation,
        standard_error=float(standard_error),
        confidence_interval=(
            float(interval[0]),
            float(interval[1]),
        ),
        observations=n,
    )