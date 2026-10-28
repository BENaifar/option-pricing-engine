from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_pipeline, get_report_service
from src.api.mappers.option_request_mapper import maturity_from_request
from src.api.schemas import PriceRequest
from src.core.exceptions import InvalidOptionRequestError
from src.pipeline.pricing_pipeline import PricingPipeline
from src.reporting.monte_carlo_accuracy.accuracy_study import MonteCarloAccuracyStudy
from src.reporting.report_service import ReportService
from tests.fake_market_data_provider import FakeMarketDataProvider
from tests.fake_pipeline import FAKE_TICKER, seeded_pipeline

FAST_PRICING = {"tree_steps": 100, "mc_paths": 2_000, "mc_steps": 8}


def _client(pipeline: PricingPipeline, report_service: ReportService | None = None) -> TestClient:
    application = create_app()
    application.dependency_overrides[get_pipeline] = lambda: pipeline
    if report_service:
        application.dependency_overrides[get_report_service] = lambda: report_service
    return TestClient(application, raise_server_exceptions=False)


def _price_body(**overrides) -> dict:
    return {"ticker": FAKE_TICKER, "strike": 100.0, "maturity": 0.5, **FAST_PRICING, **overrides}


@pytest.fixture(scope="module")
def pipeline():
    return seeded_pipeline()


@pytest.fixture(scope="module")
def client(pipeline):
    return _client(pipeline)


# ---------- health ----------

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# ---------- price ----------

def test_price_with_every_pricer(client):
    response = client.post("/price", json=_price_body())
    body = response.json()

    assert response.status_code == 200
    assert body["ticker"] == FAKE_TICKER
    assert [r["pricer"] for r in body["results"]] == ["closed_black_scholes", "binomial_tree", "monte_carlo"]
    assert all(set(r["greeks"]) == {"delta", "gamma", "theta", "rho", "vega"} for r in body["results"])


def test_statistics_only_for_monte_carlo_and_without_internal_fields(client):
    results = {r["pricer"]: r for r in client.post("/price", json=_price_body()).json()["results"]}

    assert results["closed_black_scholes"]["statistics"] is None
    assert results["binomial_tree"]["statistics"] is None
    assert set(results["monte_carlo"]["statistics"]) == {
        "variance", "standard_deviation", "standard_error", "confidence_interval", "observations"
    }


def test_response_exposes_only_documented_fields(client):
    body = client.post("/price", json=_price_body(pricers=["closed_black_scholes"])).json()

    assert set(body) == {
        "ticker", "spot", "quoted_spot", "spot_source", "strike", "maturity", "option_type", "style",
        "rate", "dividend_yield", "volatility", "market_data_timestamp", "market_data_source", "results",
    }
    assert set(body["results"][0]) == {"pricer", "price", "greeks", "statistics"}


def test_greeks_can_be_skipped(client):
    body = client.post("/price", json=_price_body(pricers=["closed_black_scholes"], greeks=False)).json()
    assert body["results"][0]["greeks"] is None


def test_variance_reduction_choice(client):
    plain, reduced = (
        client.post("/price", json=_price_body(pricers=["monte_carlo"], greeks=False, mc_variance_reduction=technique)).json()
        for technique in ("none", "control_variate")
    )
    assert reduced["results"][0]["statistics"]["standard_error"] < plain["results"][0]["statistics"]["standard_error"]


def test_expiry_is_converted_to_maturity(client):
    expiry = date.today() + timedelta(days=73)
    body = client.post("/price", json=_price_body(maturity=None, expiry=expiry.isoformat(), pricers=["closed_black_scholes"])).json()

    assert body["maturity"] == pytest.approx(73 / 365)


def test_american_option_on_the_tree(client):
    body = client.post("/price", json=_price_body(style="american", option_type="put")).json()
    assert [r["pricer"] for r in body["results"]] == ["binomial_tree"]


# ---------- request validation ----------

@pytest.mark.parametrize("overrides", [
    {"maturity": None},
    {"expiry": "2030-01-01"},
    {"ticker": ""},
    {"ticker": "A B"},
    {"ticker": "TOOLONGTICKER1"},
    {"strike": -1},
    {"mc_paths": 1},
    {"mc_confidence_level": 1.5},
    {"mc_variance_reduction": "importance_sampling"},
])
def test_invalid_requests_are_rejected_before_pricing(client, overrides):
    assert client.post("/price", json=_price_body(**overrides)).status_code == 422


def test_past_expiry(client):
    response = client.post("/price", json=_price_body(maturity=None, expiry="2020-01-01"))

    assert response.status_code == 422
    assert "must be in the future" in response.json()["detail"]


def test_monte_carlo_cannot_price_american_options(client):
    response = client.post("/price", json=_price_body(style="american", pricers=["monte_carlo"]))

    assert response.status_code == 422
    assert "binomial tree" in response.json()["detail"]


def test_maturity_mapper_never_computes_in_the_schema():
    request = PriceRequest(ticker="AAPL", strike=100, expiry=date(2026, 3, 1))

    assert request.maturity is None
    assert maturity_from_request(request, today=date(2026, 1, 1)) == pytest.approx(59 / 365)
    with pytest.raises(InvalidOptionRequestError):
        maturity_from_request(request, today=date(2026, 3, 1))


# ---------- error mapping ----------

def test_unknown_ticker_is_404():
    client = _client(PricingPipeline(provider=FakeMarketDataProvider(empty_spot=True)))
    response = client.post("/price", json=_price_body(ticker="NOPE"))

    assert response.status_code == 404
    assert "NOPE" in response.json()["detail"]


def test_unusable_market_data_is_503():
    class NoOptionsProvider(FakeMarketDataProvider):
        def fetch_options(self, ticker):
            return []

    response = _client(PricingPipeline(provider=NoOptionsProvider())).post("/price", json=_price_body(ticker="EMPTY"))

    assert response.status_code == 503
    assert "option quotes" in response.json()["detail"]


def test_unexpected_errors_do_not_leak_details():
    class BrokenPipeline:
        def price(self, **kwargs):
            raise AttributeError("'NoneType' object has no attribute 'spot'")

    response = _client(BrokenPipeline()).post("/price", json=_price_body())

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}


# ---------- market data ----------

def test_market_data(client, pipeline):
    body = client.get(f"/market-data/{FAKE_TICKER}").json()
    snapshot = pipeline.get_snapshot(FAKE_TICKER)

    assert body["spot"] == pytest.approx(snapshot.spot)
    assert body["surface_maturities"] == pytest.approx(snapshot.sigma.times)
    assert len(body["surface_vols"]) == len(body["surface_maturities"])
    assert all(len(row) == len(body["surface_strikes"]) for row in body["surface_vols"])
    assert set(body["rates"]) == {"0.0833", "0.25", "0.5", "1.0", "2.0", "5.0", "10.0", "30.0"}


def test_market_data_rejects_invalid_ticker(client):
    assert client.get("/market-data/NOT A TICKER").status_code == 422


# ---------- report ----------

def test_report_returns_a_pdf(pipeline):
    report_service = ReportService(pipeline, accuracy_study=MonteCarloAccuracyStudy(path_counts=(2_000,)))
    response = _client(pipeline, report_service).post("/report", json=_price_body(run_tests=False))

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == 'attachment; filename="FAKE_call_100_report.pdf"'
    assert response.content.startswith(b"%PDF")


def test_report_does_not_run_the_test_suite_by_default():
    from src.api.mappers.report_request_mapper import option_report_request_from_request
    from src.api.schemas import ReportRequest

    request = ReportRequest(ticker="AAPL", strike=100, maturity=0.5)

    assert option_report_request_from_request(request).run_tests is False
