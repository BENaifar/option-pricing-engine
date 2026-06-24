from dataclasses import dataclass
from datetime import date, datetime

from scipy.interpolate import PchipInterpolator

from src.time.str_to_date import safe_parse_date

@dataclass
class DividendCurve:
    issuance_dates: list[date]
    times: list[float]
    dividends: list[float]

    def q(self, t: float) -> float:
        if self._curve is None:
            self._curve = PchipInterpolator(self.times, self.dividends)

        q = self._curve(t)

        return q
    
    def get_dividends(self, start_date: str | date = datetime.now().date()) -> list[tuple[date, float]]:
        from_date = safe_parse_date(start_date)

        dividends = []

        for d, v in zip(self.issuance_dates, self.dividends):
            if from_date <= d:
                dividends.append((d, v))

        dividends_sorted = sorted(dividends, key=lambda x: x[0])

        return dividends_sorted