from datetime import datetime

import pandas as pd

from src.core.exceptions import MarketDataUnavailableError


def load_spot(df: pd.DataFrame, date: datetime):
    if df is None or df.empty:
        raise MarketDataUnavailableError("No spot price history returned")

    date = pd.to_datetime(date).normalize()

    # yfinance returns a tz-aware index; compare on plain dates
    index = df.index.tz_localize(None) if df.index.tz is not None else df.index
    closes = df["Close"][index.normalize() <= date]

    # take the last close on or before the valuation date (weekends, holidays)
    if closes.empty:
        raise MarketDataUnavailableError(
            f"Missing market data on or before {date.date()}. "
            f"Available range: {index.min().date()} → {index.max().date()}"
        )

    return float(pd.to_numeric(closes.iloc[-1]))