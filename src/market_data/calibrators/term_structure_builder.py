from dataclasses import dataclass

from scipy.interpolate import CubicSpline

from src.market_data.models.iv_quote import IVQuote


@dataclass
class TermStructureBuilder:
    K: float
    options: list[IVQuote]

    def __post_init(self):
        self.Ts, self.ivs = self._get_sorted_K_iv()
        self.curve = self.__compute_spline()

    def _get_sorted_K_iv(self):
        """Return two lists: maturities (T) and corresponding IVs sorted by T ascending."""
        if not self.options:
            return [], []

        sorted_opts = sorted(self.options, key=lambda q: q.T)
        Ts = [float(q.T) for q in sorted_opts]
        ivs = [float(q.iv) for q in sorted_opts]
        return Ts, ivs

    def __compute_spline(self):
        return CubicSpline(
            self.Ts,
            self.ivs,
            bc_type='natural'
        )