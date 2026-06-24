from datetime import datetime
import pandas as pd

from src.instruments.option_types import OptionType
from src.market_data.models.option_quote import OptionQuote
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider

def get_option_chain_snapshot(
    df: pd.DataFrame,
    valuation_date: datetime,
    expiry_date: datetime
) -> list[OptionQuote]:

    if df is None or df.empty:
        raise ValueError("Option chain DataFrame is empty")

    valuation_date = pd.to_datetime(valuation_date)
    expiry_date = pd.to_datetime(expiry_date)

    # time to maturity in years
    T = (expiry_date - valuation_date).days / 365.0

    if T <= 0:
        raise ValueError("Expiry must be after valuation date")

    result = []

    for _, row in df.iterrows():

        strike = float(row["strike"])

        # robust market price (mid if available)
        bid = row.get("bid", None)
        ask = row.get("ask", None)

        if pd.notna(bid) and pd.notna(ask) and bid > 0 and ask > 0:
            price = (bid + ask) / 2.0
        else:
            price = row.get("lastPrice", None)

        if price is None or pd.isna(price):
            continue  # skip bad quotes

        option_type = row["option_type"]

        result.append(
            OptionQuote(
                K=strike,
                T=T,
                price=float(price),
                type=option_type
            )
        )

    # sort by strike (important for surfaces / interpolation)
    result.sort(key=lambda x: x.K)

    return result

def get_all_option_quotes(
    provider: BaseMarketDataProvider,
    ticker: str,
    valuation_date: datetime
) -> list[OptionQuote]:

    quotes = []

    expiries = provider.fetch_options(ticker)

    for expiry in expiries:
        chain = provider.fetch_option_chain(ticker, expiry)

        quotes.extend(
            get_option_chain_snapshot(
                chain,
                valuation_date=valuation_date,
                expiry_date=pd.to_datetime(expiry)
            )
        )

    return quotes

def get_quotes_by_strike(
    quotes: list[OptionQuote],
    strike: float,
    option_type: OptionType | None = None,
    strike_tol: float = 1e-8
) -> list[OptionQuote]:

    result = []

    for q in quotes:

        if abs(q.K - strike) > strike_tol:
            continue

        if option_type is not None and q.type != option_type:
            continue

        result.append(q)

    result.sort(key=lambda q: q.T)

    return result

def get_quotes_by_strike_and_maturity(
    quotes: list[OptionQuote],
    strike: float,
    maturity: float,
    option_type: OptionType | None = None,
    strike_tol: float = 1e-8,
    maturity_tol: float = 1e-6
) -> list[OptionQuote]:

    result = []

    for q in quotes:

        if abs(q.K - strike) > strike_tol:
            continue

        if abs(q.T - maturity) > maturity_tol:
            continue

        if option_type is not None and q.type != option_type:
            continue

        result.append(q)

    return result