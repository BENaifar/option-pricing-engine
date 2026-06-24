import numpy as np


class Integrator:
    """
    Generic numerical integration engine for quant curves.
    Uses adaptive trapezoidal integration on a grid.
    """

    @staticmethod
    def integrate_function(f, T: float, n: int = 200) -> float:
        """
        Integrates a function f(t) from 0 to T.

        Parameters:
            f : callable
                function of time f(t)
            T : float
                upper bound (in years)
            n : int
                number of steps

        Returns:
            float: integral value
        """

        if T <= 0:
            return 0.0

        dt = T / n
        integral = 0.0

        t_prev = 0.0
        f_prev = f(0.0)

        for i in range(1, n + 1):
            t = i * dt
            f_curr = f(t)

            # trapezoid rule
            integral += 0.5 * (f_prev + f_curr) * (t - t_prev)

            t_prev = t
            f_prev = f_curr

        return integral