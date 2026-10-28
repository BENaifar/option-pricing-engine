from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SurfaceGrid:
    moneyness: np.ndarray
    maturities: np.ndarray
    vols: np.ndarray  # one row per maturity
