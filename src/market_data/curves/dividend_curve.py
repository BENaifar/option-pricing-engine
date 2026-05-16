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
        poly = PchipInterpolator(self.times, self.dividends)

        rate = poly(t)

        return rate
    
    def get_dividends(self, start_date: str | date = datetime.now().date()) -> list[tuple[date, float]]:
        from_date = safe_parse_date(start_date)

        dividends = []

        for d, v in zip(self.issuance_dates, self.dividends):
            if from_date <= d:
                dividends.append((d, v))

        dividends_sorted = sorted(dividends, key=lambda x: x[0])

        return dividends_sorted


if __name__ == "__main__":
    issuance_dates = [date(2012, 8, 9), date(2012, 11, 7), date(2013, 2, 7), date(2013, 5, 9), date(2013, 8, 8), date(2013, 11, 6), date(2014, 2, 6), date(2014, 5, 8), date(2014, 8, 7), date(2014, 11, 6), date(2015, 2, 5), date(2015, 5, 7), date(2015, 8, 6), date(2015, 11, 5), date(2016, 2, 4), date(2016, 5, 5), date(2016, 8, 4), date(2016, 11, 3), date(2017, 2, 9), date(2017, 5, 11), date(2017, 8, 10), date(2017, 11, 10), date(2018, 2, 9), date(2018, 5, 11), date(2018, 8, 10), date(2018, 11, 8), date(2019, 2, 8), date(2019, 5, 10), date(2019, 8, 9), date(2019, 11, 7), date(2020, 2, 7), date(2020, 5, 8), date(2020, 8, 7), date(2020, 11, 6), date(2021, 2, 5), date(2021, 5, 7), date(2021, 8, 6), date(2021, 11, 5), date(2022, 2, 4), date(2022, 5, 6), date(2022, 8, 5), date(2022, 11, 4), date(2023, 2, 10), date(2023, 5, 12), date(2023, 8, 11), date(2023, 11, 10), date(2024, 2, 9), date(2024, 5, 10), date(2024, 8, 12), date(2024, 11, 8), date(2025, 2, 10), date(2025, 5, 12), date(2025, 8, 11), date(2025, 11, 10), date(2026, 2, 9)]
    dividends = [0.09464286, 0.09464286, 0.09464286, 0.10892857, 0.10892857, 0.10892857, 0.10892857, 0.1175, 0.1175, 0.1175, 0.1175, 0.13, 0.13, 0.13, 0.13, 0.1425, 0.1425, 0.1425, 0.1425, 0.1575, 0.1575, 0.1575, 0.1575, 0.1825, 0.1825, 0.1825, 0.1825, 0.1925, 0.1925, 0.1925, 0.1925, 0.205, 0.205, 0.205, 0.205, 0.22, 0.22, 0.22, 0.22, 0.23, 0.23, 0.23, 0.23, 0.24, 0.24, 0.24, 0.24, 0.25, 0.25, 0.25, 0.25, 0.26, 0.26, 0.26, 0.26]
    
    curve = DividendCurve(
        issuance_dates = issuance_dates,
        times=[0.1, 0.2],
        dividends=dividends
    )

    print(curve.get_dividends("01/01/2024"))

