from dataclasses import dataclass

from scipy.interpolate import CubicSpline

@dataclass(frozen=True)
class VolatilitySmileCurve:
    maturity: float
    curve: CubicSpline   # fitted on log-moneyness ln(K / F)
    forward: float