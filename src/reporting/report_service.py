from dataclasses import dataclass, field, replace
from datetime import datetime

from src.instruments.european_option import EuropeanOption
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.models.black_scholes_model import BlackScholesModel
from src.pipeline.pricing_pipeline import ExerciseStyle, PricingPipeline
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.process.process_factory import ProcessFactory
from src.reporting.analytic_greeks import AnalyticGreeks
from src.reporting.market_comparison.live_quote_fetcher import LiveQuoteFetcher
from src.reporting.market_comparison.market_comparator import MarketComparator
from src.reporting.monte_carlo_accuracy.accuracy_result import MonteCarloAccuracyResult
from src.reporting.monte_carlo_accuracy.accuracy_study import MonteCarloAccuracyStudy
from src.reporting.option_report_request import OptionReportRequest
from src.reporting.report_data import ReportData
from src.reporting.report_warnings.stale_rates_rule import StaleRatesRule
from src.reporting.report_warnings.warning_rule import WarningRule
from src.reporting.testing.pytest_runner import PytestRunner


def default_warning_rules() -> list[WarningRule]:
    return [StaleRatesRule()]


@dataclass
class ReportService:
    pipeline: PricingPipeline
    comparator: MarketComparator | None = None
    test_runner: PytestRunner = field(default_factory=PytestRunner)
    analytic_greeks: AnalyticGreeks = field(default_factory=AnalyticGreeks)
    accuracy_study: MonteCarloAccuracyStudy = field(default_factory=MonteCarloAccuracyStudy)
    warning_rules: list[WarningRule] = field(default_factory=default_warning_rules)

    def __post_init__(self):
        if self.comparator is None:
            self.comparator = MarketComparator(LiveQuoteFetcher(self.pipeline.provider))

    def build(self, request: OptionReportRequest) -> ReportData:
        pricing = self.pipeline.price(
            ticker=request.ticker,
            strike=request.strike,
            maturity=request.maturity,
            option_type=request.option_type,
            style=request.style,
            pricers=request.pricers,
            compute_greeks=True,
            settings=request.settings,
        )
        snapshot = self.pipeline.get_snapshot(request.ticker)

        data = ReportData(
            generated_at=datetime.now(),
            pricing=pricing,
            settings=request.settings,
            snapshot=snapshot,
            bumps=self.pipeline.greeks_engine.greek_bumps_config,
            analytic_greeks=self.analytic_greeks.compute(pricing),
            market_comparison=self.comparator.compare(snapshot.ticker, snapshot),
            monte_carlo_accuracy=self._monte_carlo_accuracy(request, snapshot),
            tests=self.test_runner.run() if request.run_tests else None,
        )
        return replace(data, warnings=[w for rule in self.warning_rules if (w := rule.evaluate(data))])

    def _monte_carlo_accuracy(self, request: OptionReportRequest, snapshot: MarketDataSnapshot) -> MonteCarloAccuracyResult:
        if request.style != ExerciseStyle.EUROPEAN:
            return MonteCarloAccuracyResult(unavailable_reason="Monte Carlo does not price American options.")

        option = EuropeanOption(strike=request.strike, maturity=request.maturity, option_type=request.option_type)
        process = ProcessFactory.create(BlackScholesModel(snapshot, strike=request.strike, maturity=request.maturity))
        reference = float(ClosedBlackScholesPricer().price(option, process, snapshot.spot))

        return self.accuracy_study.run(option, process, snapshot.spot, request.settings, reference)
