import numpy as np
import pandas as pd
from datetime import date, datetime

def build_dividend_curve_inputs(
    dividend_series: pd.Series,
    valuation_date: str | date | datetime = datetime.now().date()
):
    """
    Converts yfinance dividend series into DividendCurve inputs.

    Returns:
        issuance_dates: list[date]
        times: list[float]
        dividends: list[float]
    """

    if dividend_series is None or dividend_series.empty:
        raise ValueError("Dividend series is empty or None")

    valuation_date = pd.to_datetime(valuation_date).date()

    issuance_dates = []
    times = []
    dividends = []

    for dt, value in dividend_series.items():

        d = pd.to_datetime(dt).date()

        if d < valuation_date:
            continue  # ignore past dividends (optional design choice)

        t = (d - valuation_date).days / 365.0

        issuance_dates.append(d)
        times.append(t)
        dividends.append(float(value))

    # sort by time (VERY important for interpolation stability)
    sorted_data = sorted(zip(times, issuance_dates, dividends), key=lambda x: x[0])

    if not sorted_data:
        raise ValueError("No future dividends found after valuation date")

    times, issuance_dates, dividends = zip(*sorted_data)

    return list(issuance_dates), list(times), list(dividends)
def build_dividend_yield(
    dividend_series: pd.Series | None,
    spot: float,
    valuation_date: str | date | datetime
) -> float:
    """
    Converts a historical yfinance dividend series into a continuous dividend yield.

    Uses the trailing 12 months of cash dividends: q = ln(1 + D_12m / S).
    Returns 0.0 for non-dividend paying tickers.
    """

    if dividend_series is None or dividend_series.empty:
        return 0.0

    valuation_date = pd.to_datetime(valuation_date).normalize()
    index = dividend_series.index
    index = index.tz_localize(None) if index.tz is not None else index

    mask = (index > valuation_date - pd.DateOffset(years=1)) & (index <= valuation_date)
    trailing_dividends = float(dividend_series[mask].sum())

    return float(np.log1p(trailing_dividends / spot))
