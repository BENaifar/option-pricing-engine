from dataclasses import dataclass, field

from src.reporting.market_comparison.comparison_summary import ComparisonSummary
from src.reporting.market_comparison.quote_comparison import QuoteComparison


@dataclass(frozen=True)
class MarketComparisonResult:
    comparisons: list[QuoteComparison] = field(default_factory=list)
    unavailable_reason: str | None = None

    @property
    def in_sample(self) -> list[QuoteComparison]:
        return [c for c in self.comparisons if c.in_sample]

    @property
    def out_of_sample(self) -> list[QuoteComparison]:
        return [c for c in self.comparisons if not c.in_sample]

    def summaries(self) -> list[ComparisonSummary]:
        return [
            ComparisonSummary.of("In-sample (OTM, calibration)", self.in_sample),
            ComparisonSummary.of("Out-of-sample (ITM)", self.out_of_sample),
            ComparisonSummary.of("All quotes", self.comparisons),
        ]
