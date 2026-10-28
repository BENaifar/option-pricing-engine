from dataclasses import dataclass, field
from datetime import datetime

from src.greeks.greeks import Greeks
from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.pipeline.pricing_pipeline import PricerName, PricerResult, PricingResult, PricingSettings
from src.reporting.market_comparison.market_comparison_result import MarketComparisonResult
from src.reporting.monte_carlo_accuracy.accuracy_result import MonteCarloAccuracyResult
from src.reporting.report_warnings.report_warning import ReportWarning
from src.reporting.testing.run_result import RunResult


@dataclass(frozen=True)
class ReportData:
    generated_at: datetime
    pricing: PricingResult
    settings: PricingSettings
    snapshot: MarketDataSnapshot
    bumps: GreeksBumpsConfig
    analytic_greeks: Greeks | None
    market_comparison: MarketComparisonResult
    monte_carlo_accuracy: MonteCarloAccuracyResult
    tests: RunResult | None
    warnings: list[ReportWarning] = field(default_factory=list)

    @property
    def closed_form_result(self) -> PricerResult | None:
        return self._result(PricerName.CLOSED_BLACK_SCHOLES)

    @property
    def monte_carlo_result(self) -> PricerResult | None:
        return self._result(PricerName.MONTE_CARLO)

    def _result(self, pricer: PricerName) -> PricerResult | None:
        return next((r for r in self.pricing.results if r.pricer == pricer), None)
