from dataclasses import dataclass

from scipy.interpolate import PchipInterpolator

from src.market_data.models.rate import Rate

@dataclass
class YieldCurve:
    rates: list[Rate]

    def __post_init__(self):
        self.rates = sorted(self.rates, key=lambda r: r.time_to_maturity)
        self.times = [r.time_to_maturity for r in self.rates]
        self.rates_list = [r.rate for r in self.rates]
        self._curve = None

    def r(self, t:float) -> float:
        if self._curve is None:
            self._curve = PchipInterpolator(self.times, self.rates)

        rate = self._curve(t)

        return rate
    
