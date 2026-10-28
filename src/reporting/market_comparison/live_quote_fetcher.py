from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from src.instruments.option_types import OptionType
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider
from src.reporting.market_comparison.liquidity_filter import LiquidityFilter
from src.reporting.market_comparison.market_quote import MarketQuote


@dataclass
class LiveQuoteFetcher:
    provider: BaseMarketDataProvider
    liquidity_filter: LiquidityFilter = field(default_factory=LiquidityFilter)

    def fetch(self, ticker: str, snapshot: MarketDataSnapshot) -> list[MarketQuote]:
        valuation = pd.to_datetime(datetime.fromisoformat(snapshot.timestamp))
        quotes = []

        for expiry in self.provider.fetch_options(ticker):
            T = (pd.to_datetime(expiry) - valuation).days / 365.0
            if not self.liquidity_filter.accepts_maturity(T):
                continue

            chain = self.provider.fetch_option_chain(ticker, expiry)
            quotes += [
                quote for quote in self._parse_chain(chain, T)
                if self.liquidity_filter.accepts(quote, snapshot.spot)
            ]

        return sorted(quotes, key=lambda q: (q.T, q.option_type.value, q.K))

    @staticmethod
    def _parse_chain(chain: pd.DataFrame, T: float) -> list[MarketQuote]:
        quotes = []

        for _, row in chain.iterrows():
            bid, ask = row.get("bid"), row.get("ask")
            if pd.isna(bid) or pd.isna(ask) or bid <= 0 or ask <= bid:
                continue

            option_type = OptionType.from_string(row["option_type"])
            quotes.append(MarketQuote(float(row["strike"]), T, option_type, float(bid), float(ask)))

        return quotes
