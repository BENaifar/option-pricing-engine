from datetime import datetime

import pandas as pd


def load_spot(df: pd.DataFrame, date: datetime):
    if df is None or df.empty:
        raise ValueError("DataFrame is empty or None")

    date = pd.to_datetime(date).normalize()

    if date not in df.index:
        raise KeyError(
            f"Missing market data for {date.date()}. "
            f"Available range: {df.index.min().date()} → {df.index.max().date()}"
        )

    return float(pd.to_numeric(df.at[date, "Close"]))