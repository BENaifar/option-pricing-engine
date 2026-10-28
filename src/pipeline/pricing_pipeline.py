import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.exceptions import InvalidOptionRequestError
from src.greeks.bump_and_reprice_greeks import BumpAndRepriceGreeks
from src.greeks.greeks import Greeks
from src.instruments.american_option import AmericanOption
from src.instruments.base_option import BaseOption
from src.instruments.european_option import EuropeanOption
from src.instruments.option_types import OptionType
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider
from src.market_data.providers.yahoo_market_data_provider import YahooMarketDataProvider
from src.market_data.services.market_data_service import MarketDataService
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.base_pricer import BasePricer
from src.pricers.binomial_tree import BinomialTree
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer, VarianceReductionTechnique
from src.pricers.monte_carlo_price_statistics import MonteCarloPriceStatistics
from src.process.process_factory import ProcessFactory
from src.schemes.binomial_tree_scheme import BinomialTreeScheme
from src.schemes.euler_scheme import EulerScheme
from src.schemes.exact_gbm_scheme import ExactGBMScheme


class PricerName(str, Enum):
    CLOSED_BLACK_SCHOLES = "closed_black_scholes"
    BINOMIAL_TREE = "binomial_tree"
    MONTE_CARLO = "monte_carlo"


class ExerciseStyle(str, Enum):
    EUROPEAN = "european"
    AMERICAN = "american"


class MonteCarloScheme(str, Enum):
    EXACT = "exact"
    EULER = "euler"


@dataclass
class PricingSettings:
    tree_steps: int = 1000
    mc_paths: int = 100_000
    mc_steps: int = 64
    mc_scheme: MonteCarloScheme = MonteCarloScheme.EXACT
    mc_variance_reduction: VarianceReductionTechnique = VarianceReductionTechnique.NONE
    mc_confidence_level: float = 0.95
    seed: int = 42


@dataclass(frozen=True)
class PricerResult:
    pricer: PricerName
    price: float
    greeks: Greeks | None
    statistics: MonteCarloPriceStatistics | None = None


@dataclass(frozen=True)
class PricingResult:
    ticker: str
    spot: float
    quoted_spot: float | None
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
    results: list[PricerResult]


@dataclass
class PricingPipeline:
    """
    ticker -> market data snapshot -> Black-Scholes model -> process -> pricers -> price + greeks.
    Snapshots are cached per ticker: building one hits the provider for every expiry.
    """
    provider: BaseMarketDataProvider = field(default_factory=YahooMarketDataProvider)
    snapshot_ttl_seconds: float = 900
    greeks_engine: BumpAndRepriceGreeks = field(default_factory=BumpAndRepriceGreeks)

    def __post_init__(self):
        self._snapshots: dict[str, tuple[float, MarketDataSnapshot]] = {}

    def get_snapshot(self, ticker: str, refresh: bool = False) -> MarketDataSnapshot:
        ticker = ticker.strip().upper()
        cached = self._snapshots.get(ticker)

        if cached is not None and not refresh and time.monotonic() - cached[0] < self.snapshot_ttl_seconds:
            return cached[1]

        snapshot = MarketDataService(provider=self.provider, ticker=ticker, valuation_at=datetime.now()).get_market_data_snapshot()
        self._snapshots[ticker] = (time.monotonic(), snapshot)

        return snapshot

    def price(
        self,
        ticker: str,
        strike: float,
        maturity: float,
        option_type: OptionType,
        style: ExerciseStyle = ExerciseStyle.EUROPEAN,
        pricers: list[PricerName] | None = None,
        compute_greeks: bool = True,
        settings: PricingSettings | None = None,
    ) -> PricingResult:
        settings = settings or PricingSettings()
        pricers = pricers or self.default_pricers(style)

        option = self.build_option(strike, maturity, option_type, style)
        self._validate_pricers(option, pricers)

        market_data = self.get_snapshot(ticker)
        model = BlackScholesModel(market_data, strike=strike, maturity=maturity)
        process = ProcessFactory.create(model)

        results = []
        for name in pricers:
            pricer = self.build_pricer(name, settings)
            statistics = self._statistics(pricer, option, process, market_data.spot, settings)
            price = statistics.price if statistics else float(pricer.price(option, process, market_data.spot))
            greeks = self.greeks_engine.compute(pricer, option, process, market_data.spot) if compute_greeks else None
            results.append(PricerResult(pricer=name, price=price, greeks=greeks, statistics=statistics))

        return PricingResult(
            ticker=market_data.ticker,
            spot=market_data.spot,
            quoted_spot=market_data.quoted_spot,
            spot_source=market_data.spot_source,
            strike=strike,
            maturity=maturity,
            option_type=option_type,
            style=style,
            rate=model.r,
            dividend_yield=model.q,
            volatility=model.sigma,
            market_data_timestamp=market_data.timestamp,
            market_data_source=market_data.source,
            results=results,
        )

    @staticmethod
    def _statistics(pricer: BasePricer, option: BaseOption, process, spot: float, settings: PricingSettings) -> MonteCarloPriceStatistics | None:
        if not isinstance(pricer, MonteCarloPricer):
            return None
        return pricer.price_with_statistics(option, process, spot, confidence_level=settings.mc_confidence_level)

    @staticmethod
    def default_pricers(style: ExerciseStyle) -> list[PricerName]:
        if style == ExerciseStyle.AMERICAN:
            return [PricerName.BINOMIAL_TREE]
        return [PricerName.CLOSED_BLACK_SCHOLES, PricerName.BINOMIAL_TREE, PricerName.MONTE_CARLO]

    @staticmethod
    def build_option(strike: float, maturity: float, option_type: OptionType, style: ExerciseStyle) -> BaseOption:
        if style == ExerciseStyle.AMERICAN:
            return AmericanOption(strike=strike, maturity=maturity, option_type=option_type)
        return EuropeanOption(strike=strike, maturity=maturity, option_type=option_type)

    @staticmethod
    def build_pricer(name: PricerName, settings: PricingSettings) -> BasePricer:
        if name == PricerName.CLOSED_BLACK_SCHOLES:
            return ClosedBlackScholesPricer()
        if name == PricerName.BINOMIAL_TREE:
            return BinomialTree(scheme=BinomialTreeScheme(), steps=settings.tree_steps)
        if name == PricerName.MONTE_CARLO:
            scheme = ExactGBMScheme() if settings.mc_scheme == MonteCarloScheme.EXACT else EulerScheme()
            return MonteCarloPricer(
                scheme=scheme,
                paths=settings.mc_paths,
                n_steps=settings.mc_steps,
                seed=settings.seed,
                variance_reduction_technique=settings.mc_variance_reduction,
            )

        raise ValueError(f"Unsupported pricer: {name}")

    @staticmethod
    def _validate_pricers(option: BaseOption, pricers: list[PricerName]):
        if option.is_american():
            unsupported = [p.value for p in pricers if p != PricerName.BINOMIAL_TREE]
            if unsupported:
                raise InvalidOptionRequestError(f"American options can only be priced with the binomial tree, not {unsupported}")
