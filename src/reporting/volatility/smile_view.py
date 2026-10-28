from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SmileView:
    maturity: float
    quoted_moneyness: np.ndarray
    quoted_vols: np.ndarray
    fitted_moneyness: np.ndarray
    fitted_vols: np.ndarray
