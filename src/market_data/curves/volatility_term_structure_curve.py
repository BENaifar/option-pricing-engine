from dataclasses import dataclass

from scipy.interpolate import CubicSpline

@dataclass(frozen=True)
class VolatilityTermStructureCurve:
    K: float
    curve: CubicSpline