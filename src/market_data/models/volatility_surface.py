from bisect import bisect_left
from dataclasses import dataclass

import numpy as np
from scipy.interpolate import interp1d

from src.market_data.curves.volatility_smile_curve import VolatilitySmileCurve
from src.market_data.curves.volatility_term_structure_curve import VolatilityTermStructureCurve
from src.market_data.models.volatility_model import VolatilityModel


@dataclass
class VolatilitySurfaceBuilder(VolatilityModel):
    smiles: dict[float, VolatilitySmileCurve]
    terms: dict[float, VolatilityTermStructureCurve]
    times: list[float]
    strikes: list[float]

    def __post_init__(self):
        if self.times:
            self.times = sorted(self.times)
        if self.strikes:
            self.strikes = sorted(self.strikes)

    def find_inferior_superior(self, t) -> tuple[float | None, float | None]:
        """
        Returns:
            (inferior, superior)
            inferior = greatest value <= t
            superior = smallest value >= t
        """
        if not self.times:
            return None, None

        idx = bisect_left(self.times, t)

        # exact match case
        if idx < len(self.times) and self.times[idx] == t:
            return t, t

        inferior = self.times[idx - 1] if idx > 0 else None
        superior = self.times[idx] if idx < len(self.times) else None

        return inferior, superior
    
    def get_smile_at_K(self, K, T):
        return self.smiles[T].curve(K)
    
    def _ensure_time_bounds(self, T_inf, T_sup):
        """Ensure time bounds are set to valid extremes if None."""
        if T_inf is None:
            T_inf = self.times[0]
        if T_sup is None:
            T_sup = self.times[-1]
        return T_inf, T_sup
    
    def _get_volatilities(self, K, T_inf, T_sup):
        """Retrieve volatilities at inferior and superior time bounds."""
        sigma_inf = self.get_smile_at_K(K, T_inf)
        sigma_sup = self.get_smile_at_K(K, T_sup)
        return sigma_inf, sigma_sup
    
    def _convert_vol_to_variance(self, sigma_inf, sigma_sup, T_inf, T_sup):
        """Convert volatilities to variances."""
        w_inf = sigma_inf ** 2 * T_inf
        w_sup = sigma_sup ** 2 * T_sup
        return w_inf, w_sup
    
    def _interpolate_variance(self, w_inf, w_sup, T_inf, T_sup, T):
        """Interpolate variance across time bounds."""
        return interp1d(
            [T_inf, T_sup],
            [w_inf, w_sup],
            kind="linear"
        )(T)
    
    def _convert_variance_to_vol(self, w_interp, T):
        """Convert interpolated variance back to volatility."""
        return np.sqrt(w_interp / T)
    
    def _interpolate_at_T(self, K, T):
        """Interpolate volatility at time T for strike K."""
        T_inf, T_sup = self.find_inferior_superior(T)

        if T_inf == T_sup:
            return self.get_smile_at_K(K, T)

        T_inf, T_sup = self._ensure_time_bounds(T_inf, T_sup)
        sigma_inf, sigma_sup = self._get_volatilities(K, T_inf, T_sup)
        w_inf, w_sup = self._convert_vol_to_variance(sigma_inf, sigma_sup, T_inf, T_sup)
        w_interp = self._interpolate_variance(w_inf, w_sup, T_inf, T_sup, T)
        sigma = self._convert_variance_to_vol(w_interp, T)

        return float(sigma)
    
    def get_vol(self, K, T):
        return self._interpolate_at_T(K, T)