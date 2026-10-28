import time

import pandas as pd

from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider
from src.market_data.services.market_data_service import MarketDataService
from src.pipeline.pricing_pipeline import PricingPipeline
from tests.fake_market_data_provider import VALUATION_DATE, FakeMarketDataProvider

FAKE_TICKER = "FAKE"


class SpreadProvider(FakeMarketDataProvider):
    """Fake chain with a 1% bid/ask spread around the model price."""

    def fetch_option_chain(self, ticker, date) -> pd.DataFrame:
        chain = super().fetch_option_chain(ticker, date)
        chain["bid"], chain["ask"] = chain["bid"] * 0.995, chain["ask"] * 1.005
        return chain


def seeded_pipeline(provider: BaseMarketDataProvider | None = None) -> PricingPipeline:
    """Pipeline whose FAKE snapshot is valued at VALUATION_DATE (the pipeline would otherwise value at now)."""
    provider = provider or SpreadProvider()
    pipeline = PricingPipeline(provider=provider)
    snapshot = MarketDataService(provider=provider, ticker=FAKE_TICKER, valuation_at=VALUATION_DATE).get_market_data_snapshot()
    pipeline._snapshots[FAKE_TICKER] = (time.monotonic(), snapshot)
    return pipeline
