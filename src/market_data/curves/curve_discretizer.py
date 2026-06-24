import numpy as np


class CurveDiscretizer:
    """
    Converts continuous curve objects into discrete grids.
    """

    @staticmethod
    def discretize(curve, grid: np.ndarray):
        """
        Generic discretization using curve.r(t) or curve.q(t)

        Parameters:
            curve: object with method value(t) OR r(t)/q(t)
            grid: np.ndarray of time points

        Returns:
            (grid, values)
        """

        values = np.array([curve.value(t) for t in grid])
        return grid, values