import numpy as np


class ForwardPricing:

    @staticmethod
    def build_grid(T: float, n: int = 50):
        return np.linspace(0, T, n)

    @staticmethod
    def forward_price(S0, yield_curve, dividend_curve, T: float, n: int = 50):
        grid = ForwardPricing.build_grid(T, n)

        r_vals = np.array([yield_curve.r(t) for t in grid])
        q_vals = np.array([dividend_curve.q(t) for t in grid])

        net = r_vals - q_vals

        dt = np.diff(grid)
        avg = 0.5 * (net[:-1] + net[1:])

        integral = np.sum(avg * dt)

        return S0 * np.exp(integral)