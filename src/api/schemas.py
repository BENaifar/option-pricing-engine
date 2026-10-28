from datetime import date

from pydantic import BaseModel, Field, model_validator

from src.instruments.option_types import OptionType
from src.pipeline.pricing_pipeline import ExerciseStyle, MonteCarloScheme, PricerName
from src.pricers.monte_carlo import VarianceReductionTechnique

TICKER_PATTERN = r"^[A-Za-z0-9.\-^=]{1,12}$"


class PriceRequest(BaseModel):
    ticker: str = Field(pattern=TICKER_PATTERN, examples=["AAPL"], description="1 to 12 letters, digits, '.', '-', '^' or '='.")
    strike: float = Field(gt=0)
    maturity: float | None = Field(default=None, gt=0, description="Time to maturity in years. Give this or `expiry`.")
    expiry: date | None = Field(default=None, description="Expiry date. Give this or `maturity`.")
    option_type: OptionType = OptionType.CALL
    style: ExerciseStyle = ExerciseStyle.EUROPEAN
    pricers: list[PricerName] | None = Field(default=None, description="Defaults to every pricer that supports the style.")
    greeks: bool = True

    tree_steps: int = Field(default=1000, gt=0, le=5000)
    mc_paths: int = Field(default=100_000, ge=2, le=2_000_000)
    mc_steps: int = Field(default=64, gt=0, le=1000)
    mc_scheme: MonteCarloScheme = MonteCarloScheme.EXACT
    mc_variance_reduction: VarianceReductionTechnique = VarianceReductionTechnique.NONE
    mc_confidence_level: float = Field(default=0.95, gt=0, lt=1)
    seed: int = Field(default=42, ge=0)

    @model_validator(mode="after")
    def _exactly_one_of_maturity_or_expiry(self):
        if (self.maturity is None) == (self.expiry is None):
            raise ValueError("Give exactly one of `maturity` (years) or `expiry` (date).")
        return self


class ReportRequest(PriceRequest):
    run_tests: bool = Field(default=False, description="Run the offline test suite and include its results (adds ~30-60 s).")


class GreeksResponse(BaseModel):
    delta: float | None
    gamma: float | None
    theta: float | None
    rho: float | None
    vega: float | None


class MonteCarloStatisticsResponse(BaseModel):
    variance: float
    standard_deviation: float
    standard_error: float
    confidence_interval: tuple[float, float]
    observations: int


class PricerResultResponse(BaseModel):
    pricer: PricerName
    price: float
    greeks: GreeksResponse | None
    statistics: MonteCarloStatisticsResponse | None = Field(default=None, description="Monte Carlo only.")


class PriceResponse(BaseModel):
    ticker: str
    spot: float = Field(description="Spot used for pricing.")
    quoted_spot: float | None = Field(description="Equity feed price, before the put-call parity adjustment.")
    spot_source: str | None
    strike: float
    maturity: float
    option_type: OptionType
    style: ExerciseStyle
    rate: float
    dividend_yield: float
    volatility: float
    market_data_timestamp: str | None
    market_data_source: str | None
    results: list[PricerResultResponse]


class MarketDataResponse(BaseModel):
    ticker: str
    spot: float
    quoted_spot: float | None
    spot_source: str | None
    timestamp: str | None
    source: str | None
    rates: dict[str, float] = Field(description="Zero rate by tenor (years).")
    dividend_yield: float = Field(description="Dividend / carry yield q at 1 year.")
    dividend_source: str | None
    surface_maturities: list[float]
    surface_strikes: list[float]
    surface_vols: list[list[float]] = Field(description="Rows: maturities, columns: strikes.")
