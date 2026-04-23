from dataclasses import dataclass
from enum import Enum

class GREEKS(Enum):
    DELTA = "delta"
    GAMMA = "gamma"
    THETA = "theta"
    RHO = "rho"
    VEGA = "vega"

@dataclass(frozen=True)
class Greeks:
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    rho: float | None = None
    vega: float | None = None

    