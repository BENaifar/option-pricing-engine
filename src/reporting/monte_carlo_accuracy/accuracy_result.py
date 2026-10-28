from dataclasses import dataclass, field

from src.pricers.monte_carlo import VarianceReductionTechnique
from src.reporting.monte_carlo_accuracy.accuracy_run import AccuracyRun


@dataclass(frozen=True)
class MonteCarloAccuracyResult:
    reference_price: float | None = None
    confidence_level: float = 0.95
    runs: list[AccuracyRun] = field(default_factory=list)
    unavailable_reason: str | None = None

    def variance_reduction_factor(self, run: AccuracyRun) -> float | None:
        """Variance without reduction divided by variance with it, at the same number of paths."""
        baseline = next(
            (r for r in self.runs if r.paths == run.paths and r.technique == VarianceReductionTechnique.NONE),
            None,
        )
        if baseline is None or run.statistics.variance == 0:
            return None
        return baseline.statistics.variance / run.statistics.variance
