from datetime import date, datetime

from scipy.interpolate import PchipInterpolator

from src.time.str_to_date import safe_parse_date

class DividendCurve:
    def __init__(
        self,
        issuance_dates: list[date] | None,
        times: list[float] | None,
        dividends: list[float] | float,
    ):
        # Validate issuance_dates
        if issuance_dates is not None:
            if not isinstance(issuance_dates, list):
                raise TypeError("issuance_dates must be a list of date objects or None.")
            if not all(isinstance(d, date) for d in issuance_dates):
                raise TypeError("All elements of issuance_dates must be date objects.")

        # Validate times
        if times is not None:
            if not isinstance(times, list):
                raise TypeError("times must be a list of floats or None.")
            if not all(isinstance(t, (int, float)) for t in times):
                raise TypeError("All elements of times must be numeric.")
            times = [float(t) for t in times]

        # Validate dividends
        if isinstance(dividends, (int, float)):
            dividends = float(dividends)
        elif isinstance(dividends, list):
            if not all(isinstance(d, (int, float)) for d in dividends):
                raise TypeError("All elements of dividends must be numeric.")
            dividends = [float(d) for d in dividends]
        else:
            raise TypeError("dividends must be a float or a list of floats.")

        # Cross-validation
        if issuance_dates is not None and times is not None:
            if len(issuance_dates) != len(times):
                raise ValueError("issuance_dates and times must have the same length.")

        if isinstance(dividends, list):
            if issuance_dates is not None and len(dividends) != len(issuance_dates):
                raise ValueError("dividends and issuance_dates must have the same length.")
            if times is not None and len(dividends) != len(times):
                raise ValueError("dividends and times must have the same length.")

        self.issuance_dates = issuance_dates
        self.times = times
        self.dividends = dividends
        self._curve = None

    def q(self, t: float) -> float:
        if type(self.dividends) is float:
            return self.dividends
        else:
            if self._curve is None:
                self._curve = PchipInterpolator(self.times, self.dividends)

            # flat extrapolation outside the calibrated maturities
            t = min(max(t, self.times[0]), self.times[-1])
            q = self._curve(t)

            return float(q)
    
    def get_dividends(self, start_date: str | date = datetime.now().date()) -> list[tuple[date, float]]:
        from_date = safe_parse_date(start_date)

        dividends = []

        for d, v in zip(self.issuance_dates, self.dividends):
            if from_date <= d:
                dividends.append((d, v))

        dividends_sorted = sorted(dividends, key=lambda x: x[0])

        return dividends_sorted