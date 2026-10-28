from dataclasses import dataclass

from src.instruments.american_option import AmericanOption
from src.instruments.base_option import BaseOption
from src.instruments.european_option import EuropeanOption
from src.instruments.option_types import OptionType
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.base_pricer import BasePricer
from src.pricers.binomial_tree import BinomialTree
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.process.process_factory import ProcessFactory
from src.reporting.market_comparison.market_quote import MarketQuote
from src.reporting.market_comparison.quote_comparison import QuoteComparison
from src.schemes.binomial_tree_scheme import BinomialTreeScheme


@dataclass
class QuoteRepricer:
    """
    OTM quotes are in-sample: the volatility surface is calibrated on them.
    Listed equity options are American, so ITM puts are repriced with early exercise.
    """
    tree_steps: int = 500

    def reprice(self, snapshot: MarketDataSnapshot, quote: MarketQuote) -> QuoteComparison:
        in_sample = quote.is_otm(snapshot.spot)
        american = not in_sample and quote.option_type == OptionType.PUT

        process = ProcessFactory.create(BlackScholesModel(snapshot, strike=quote.K, maturity=quote.T))
        price = self._pricer(american).price(self._option(quote, american), process, snapshot.spot)

        return QuoteComparison(quote, float(price), in_sample, american)

    def reprice_all(self, snapshot: MarketDataSnapshot, quotes: list[MarketQuote]) -> list[QuoteComparison]:
        return [self.reprice(snapshot, quote) for quote in quotes]

    def _pricer(self, american: bool) -> BasePricer:
        if american:
            return BinomialTree(scheme=BinomialTreeScheme(), steps=self.tree_steps)
        return ClosedBlackScholesPricer()

    @staticmethod
    def _option(quote: MarketQuote, american: bool) -> BaseOption:
        option_class = AmericanOption if american else EuropeanOption
        return option_class(strike=quote.K, maturity=quote.T, option_type=quote.option_type)
