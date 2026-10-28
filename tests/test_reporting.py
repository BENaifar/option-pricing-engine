from dataclasses import replace

import pytest

from src.instruments.option_types import OptionType
from src.pipeline.pricing_pipeline import PricingSettings
from src.reporting.market_comparison.comparison_summary import ComparisonSummary
from src.reporting.market_comparison.liquidity_filter import LiquidityFilter
from src.reporting.market_comparison.market_comparison_result import MarketComparisonResult
from src.reporting.market_comparison.market_quote import MarketQuote
from src.reporting.monte_carlo_accuracy.accuracy_study import MonteCarloAccuracyStudy
from src.reporting.option_report_request import OptionReportRequest
from src.reporting.pdf.pdf_report_renderer import PdfReportRenderer
from src.reporting.report_service import ReportService
from src.reporting.report_warnings.report_warning import ReportWarning
from src.reporting.report_warnings.stale_rates_rule import StaleRatesRule
from src.reporting.testing.case_result import CaseOutcome
from src.reporting.testing.junit_parser import JUnitParser
from src.reporting.testing.pytest_runner import PytestRunner
from src.reporting.testing.run_result import RunResult
from src.reporting.testing.suite_catalog import SUITE_CATALOG
from src.reporting.volatility.volatility_view_builder import VolatilityViewBuilder
from src.pipeline.pricing_pipeline import ExerciseStyle
from src.pricers.monte_carlo import VarianceReductionTechnique
from tests.fake_market_data_provider import SPOT, VALUATION_DATE, true_vol
from tests.fake_pipeline import seeded_pipeline


@pytest.fixture
def fake_pipeline():
    return seeded_pipeline()


@pytest.fixture
def report_service(fake_pipeline):
    return ReportService(fake_pipeline, accuracy_study=MonteCarloAccuracyStudy(path_counts=(2_000, 8_000)))


def _request(style=ExerciseStyle.EUROPEAN):
    return OptionReportRequest(
        ticker="FAKE", strike=SPOT, maturity=0.5, option_type=OptionType.CALL, style=style,
        settings=PricingSettings(tree_steps=200, mc_paths=20_000, mc_steps=16), run_tests=False,
    )


@pytest.fixture
def report_data(report_service):
    return report_service.build(_request())


# ---------- market comparison ----------

def test_market_quote():
    put = MarketQuote(K=95.0, T=0.5, option_type=OptionType.PUT, bid=1.9, ask=2.1)

    assert put.mid == pytest.approx(2.0)
    assert put.relative_spread == pytest.approx(0.1)
    assert put.is_otm(spot=100.0)
    assert not put.is_otm(spot=90.0)


def test_liquidity_filter():
    liquidity_filter = LiquidityFilter()
    tight = MarketQuote(K=100.0, T=0.5, option_type=OptionType.CALL, bid=9.9, ask=10.1)
    wide = MarketQuote(K=100.0, T=0.5, option_type=OptionType.CALL, bid=8.0, ask=12.0)
    far = MarketQuote(K=150.0, T=0.5, option_type=OptionType.CALL, bid=0.99, ask=1.01)

    assert liquidity_filter.accepts(tight, spot=100.0)
    assert not liquidity_filter.accepts(wide, spot=100.0)
    assert not liquidity_filter.accepts(far, spot=100.0)
    assert not liquidity_filter.accepts_maturity(7 / 365)


def test_comparison_summary_of_nothing():
    summary = ComparisonSummary.of("empty", [])
    assert summary.count == 0


def test_market_comparison_on_a_consistent_market(report_data):
    """The synthetic quotes come from the model itself: every quote must be repriced inside its spread."""
    result = report_data.market_comparison

    assert result.unavailable_reason is None
    assert ComparisonSummary.of("in", result.in_sample).hit_rate == 1.0
    assert len(result.out_of_sample) > 0
    assert any(c.american for c in result.out_of_sample)


# ---------- report data ----------

def test_report_data_contents(report_data):
    assert [r.pricer.value for r in report_data.pricing.results] == ["closed_black_scholes", "binomial_tree", "monte_carlo"]
    assert all(r.greeks is not None for r in report_data.pricing.results)
    assert report_data.analytic_greeks.delta == pytest.approx(report_data.closed_form_result.greeks.delta, rel=1e-3)
    assert report_data.tests is None


# ---------- test results ----------

def test_junit_parser(tmp_path):
    xml = tmp_path / "results.xml"
    xml.write_text(
        '<testsuites><testsuite>'
        '<testcase classname="tests.test_invariants.TestInvariants" name="test_a" time="0.5"/>'
        '<testcase classname="tests.test_validation" name="test_b" time="0.1"><failure message="boom"/></testcase>'
        '<testcase classname="tests.test_validation" name="test_c" time="0"><skipped message="later"/></testcase>'
        '</testsuite></testsuites>'
    )

    cases = JUnitParser().parse(xml)

    assert [c.outcome for c in cases["test_invariants"]] == [CaseOutcome.PASSED]
    assert [c.outcome for c in cases["test_validation"]] == [CaseOutcome.FAILED, CaseOutcome.SKIPPED]
    assert cases["test_validation"][0].message == "boom"


def test_runner_lists_every_catalogued_suite():
    suites = PytestRunner()._suites({"test_unknown": []})
    assert [s.module for s in suites] == list(SUITE_CATALOG) + ["test_unknown"]


# ---------- pdf ----------

def test_pdf_renders(report_data):
    pdf = PdfReportRenderer().render_bytes(report_data)

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 10_000


def test_pdf_renders_without_market_comparison_or_tests(report_data):
    data = replace(
        report_data,
        market_comparison=MarketComparisonResult(unavailable_reason="market closed"),
        tests=RunResult("pytest", 0.0, error="pytest not installed"),
    )

    assert PdfReportRenderer().render_bytes(data).startswith(b"%PDF")


# ---------- monte carlo accuracy ----------

def test_monte_carlo_statistics_reach_the_report(report_data):
    statistics = report_data.monte_carlo_result.statistics

    assert statistics.price == report_data.monte_carlo_result.price
    assert statistics.observations == 20_000


def test_accuracy_study_runs_every_technique_and_path_count(report_data):
    result = report_data.monte_carlo_accuracy

    assert [(r.technique, r.paths) for r in result.runs] == [(t, n) for t in MonteCarloAccuracyStudy.techniques for n in (2_000, 8_000)]
    assert all(r.statistics.standard_error > 0 for r in result.runs)


def test_variance_reduction_factors(report_data):
    result = report_data.monte_carlo_accuracy
    factors = {(r.technique, r.paths): result.variance_reduction_factor(r) for r in result.runs}

    assert factors[(VarianceReductionTechnique.NONE, 8_000)] == pytest.approx(1.0)
    assert factors[(VarianceReductionTechnique.ANTITHETIC, 8_000)] > 1
    assert factors[(VarianceReductionTechnique.CONTROL_VARIATE, 8_000)] > 1


def test_accuracy_study_is_skipped_for_american_options(report_service):
    data = report_service.build(_request(ExerciseStyle.AMERICAN))
    assert data.monte_carlo_accuracy.unavailable_reason is not None


# ---------- warnings ----------

def test_rates_on_the_valuation_date_raise_no_warning(report_data):
    assert report_data.snapshot.rate.as_of == VALUATION_DATE.date()
    assert report_data.warnings == []


def test_stale_rates_raise_a_warning(report_data):
    later = replace(report_data, snapshot=replace(report_data.snapshot, timestamp="2026-03-01 10:00:00"))

    warning = StaleRatesRule(max_age_days=7).evaluate(later)

    assert warning is not None
    assert "2026-01-15" in warning.message and "45 days" in warning.message


def test_flat_rates_raise_no_warning(report_data, standard_market):
    flat = replace(report_data, snapshot=standard_market)
    assert StaleRatesRule().evaluate(flat) is None


# ---------- volatility views ----------

def test_smiles_go_through_the_calibration_quotes(report_data):
    smiles = VolatilityViewBuilder().smiles(report_data.snapshot)

    assert 0 < len(smiles) <= 6
    for smile in smiles:
        strikes = smile.quoted_moneyness * SPOT
        assert smile.quoted_vols == pytest.approx([true_vol(K) for K in strikes], abs=1e-5)


def test_surface_grid(report_data):
    builder = VolatilityViewBuilder(grid_points=11)
    grid = builder.surface(report_data.snapshot)

    assert grid.vols.shape == (len(report_data.snapshot.sigma.times), 11)
    assert builder.surface(replace(report_data.snapshot, sigma=None)) is None


def test_pdf_renders_with_warnings(report_data):
    data = replace(report_data, warnings=[ReportWarning("Stale interest rates", "rates end on 2026-05-04")])
    assert PdfReportRenderer().render_bytes(data).startswith(b"%PDF")
