MATURITY_MAP = {
    "DGS1M": 1/12,
    "DGS3M": 3/12,
    "DGS6M": 6/12,
    "DGS1": 1,
    "DGS2": 2,
    "DGS5": 5,
    "DGS10": 10,
    "DGS30": 30
}

import pandas as pd

from src.core.exceptions import MarketDataUnavailableError

from src.market_data.models.rate import Rate

def build_rate_curve(date, dfs: dict):
    """
    dfs: dict like {"DGS1": df1, "DGS10": df2, ...}
    date: datetime
    """

    results = []

    date = pd.to_datetime(date).normalize()

    for name, df in dfs.items():

        if df is None or df.empty:
            raise MarketDataUnavailableError(f"{name}: rate file is empty")

        if name not in MATURITY_MAP:
            raise ValueError(f"Unknown maturity mapping for {name}")

        # last available rate on or before the valuation date
        series = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna()
        series = series[series.index <= date]

        if series.empty:
            raise MarketDataUnavailableError(f"{name}: no rate on or before {date.date()}")

        # already in decimal (converted by the provider)
        rate_value = float(series.iloc[-1])

        results.append(
            Rate(
                time_to_maturity=MATURITY_MAP[name],
                rate=rate_value,
                as_of=series.index[-1].date()
            )
        )

    # sort by maturity
    results.sort(key=lambda x: x.time_to_maturity)

    return results


#### CALLLLLLL ###
# dfs = {
#     "DGS1": df1,
#     "DGS2": df2,
#     "DGS3M": df3,
#     "DGS6M": df4,
#     "DGS1M": df5,
#     "DGS5": df6,
#     "DGS10": df7,
#     "DGS30": df8
# }

# curve = build_rate_curve("2025-01-10", dfs)