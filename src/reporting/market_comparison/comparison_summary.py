from dataclasses import dataclass

import numpy as np

from src.reporting.market_comparison.quote_comparison import QuoteComparison


@dataclass(frozen=True)
class ComparisonSummary:
    label: str
    count: int
    hit_rate: float
    mean_absolute_error: float
    median_absolute_relative_error: float

    @classmethod
    def of(cls, label: str, comparisons: list[QuoteComparison]) -> "ComparisonSummary":
        if not comparisons:
            return cls(label, 0, float("nan"), float("nan"), float("nan"))

        return cls(
            label=label,
            count=len(comparisons),
            hit_rate=float(np.mean([c.inside_spread for c in comparisons])),
            mean_absolute_error=float(np.mean([abs(c.error) for c in comparisons])),
            median_absolute_relative_error=float(np.median([abs(c.relative_error) for c in comparisons])),
        )
