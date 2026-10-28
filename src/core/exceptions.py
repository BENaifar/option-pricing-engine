class PricingEngineError(Exception):
    """Base class for errors caused by the request or the market data, not by a bug in the engine."""


class TickerNotFoundError(PricingEngineError):
    """The provider returned no data for the ticker."""


class MarketDataUnavailableError(PricingEngineError):
    """Market data exists for the ticker but is missing, stale or unusable for pricing."""


class InvalidOptionRequestError(PricingEngineError):
    """The option or pricer combination cannot be priced as requested."""
