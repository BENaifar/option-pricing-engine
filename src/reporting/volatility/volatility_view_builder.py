from dataclasses import dataclass

import numpy as np

from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.reporting.volatility.smile_view import SmileView
from src.reporting.volatility.surface_grid import SurfaceGrid


@dataclass(frozen=True)
class VolatilityViewBuilder:
    """Plot-ready views of the snapshot surface, with moneyness expressed as K / spot."""
    max_smiles: int = 6
    min_moneyness: float = 0.8
    max_moneyness: float = 1.2
    grid_points: int = 41

    def smiles(self, snapshot: MarketDataSnapshot) -> list[SmileView]:
        smiles = getattr(snapshot.sigma, "smiles", {})
        if not smiles:
            return []

        maturities = sorted(smiles)
        picked = np.unique(np.linspace(0, len(maturities) - 1, min(self.max_smiles, len(maturities))).round().astype(int))
        return [self._smile(smiles[maturities[i]], snapshot.spot) for i in picked]

    def surface(self, snapshot: MarketDataSnapshot) -> SurfaceGrid | None:
        maturities = np.array(sorted(getattr(snapshot.sigma, "smiles", {})))
        if maturities.size == 0:
            return None

        moneyness = np.linspace(self.min_moneyness, self.max_moneyness, self.grid_points)
        vols = np.array([[snapshot.sigma.get_vol(m * snapshot.spot, T) for m in moneyness] for T in maturities])
        return SurfaceGrid(moneyness, maturities, vols)

    def _smile(self, smile, spot: float) -> SmileView:
        knots = smile.curve.x
        quoted_moneyness = smile.forward * np.exp(knots) / spot
        in_range = (quoted_moneyness >= self.min_moneyness) & (quoted_moneyness <= self.max_moneyness)

        fitted_log_moneyness = np.linspace(knots[0], knots[-1], 200)
        fitted_moneyness = smile.forward * np.exp(fitted_log_moneyness) / spot
        fitted_in_range = (fitted_moneyness >= self.min_moneyness) & (fitted_moneyness <= self.max_moneyness)

        return SmileView(
            maturity=smile.maturity,
            quoted_moneyness=quoted_moneyness[in_range],
            quoted_vols=smile.curve(knots)[in_range],
            fitted_moneyness=fitted_moneyness[fitted_in_range],
            fitted_vols=smile.curve(fitted_log_moneyness)[fitted_in_range],
        )
