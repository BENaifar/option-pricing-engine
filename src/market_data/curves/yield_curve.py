from dataclasses import dataclass
from datetime import date

from scipy.interpolate import PchipInterpolator

from src.market_data.models.rate import Rate

@dataclass
class YieldCurve:
    rates: list[Rate] | float

    def __post_init__(self):
        if type(self.rates) is not float:
            self.rates = sorted(self.rates, key=lambda r: r.time_to_maturity)
            self.times = [r.time_to_maturity for r in self.rates]
            self.rates_list = [r.rate for r in self.rates]
            self._curve = None

    @property
    def as_of(self) -> date | None:
        """Date of the oldest quote in the curve, None for a flat curve or undated rates."""
        if type(self.rates) is float:
            return None
        dates = [r.as_of for r in self.rates if r.as_of is not None]
        return min(dates) if dates else None

    def r(self, t:float) -> float:
        if type(self.rates) is float:
            return self.rates
        if self._curve is None:
            self._curve = PchipInterpolator(self.times, self.rates_list)

        # flat extrapolation outside the quoted maturities
        t = min(max(t, self.times[0]), self.times[-1])
        rate = self._curve(t)

        return float(rate)
    
