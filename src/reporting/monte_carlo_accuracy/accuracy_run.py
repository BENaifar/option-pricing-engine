from dataclasses import dataclass

from src.pricers.monte_carlo import VarianceReductionTechnique
from src.pricers.monte_carlo_price_statistics import MonteCarloPriceStatistics


@dataclass(frozen=True)
class AccuracyRun:
    technique: VarianceReductionTechnique
    paths: int
    statistics: MonteCarloPriceStatistics
    runtime_seconds: float

    def contains(self, price: float) -> bool:
        low, high = self.statistics.confidence_interval
        return low <= price <= high
