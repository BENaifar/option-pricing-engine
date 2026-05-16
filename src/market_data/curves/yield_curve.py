from dataclasses import dataclass

from scipy.interpolate import PchipInterpolator

@dataclass
class YieldCurve:
    times: list[float]
    rates: list[float]

    def r(self, t:float) -> float:
        poly = PchipInterpolator(self.times, self.rates)

        rate = poly(t)

        return rate
    
