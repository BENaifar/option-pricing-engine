import numpy as np


class NewtonRaphson:
    
    def newton_raphson(self, func, dfunc, x0, tol=1e-8, max_iter=100):
        """
        Newton-Raphson root finding method.
        
        Parameters:
            func     : callable, f(x)
            dfunc    : callable, derivative f'(x)
            x0       : float, initial guess
            tol      : float, absolute tolerance for convergence
            max_iter : int, maximum iterations
        
        Returns:
            root     : float, estimated root
            iters    : int, iterations used
        """

        x = x0
        for i in range(max_iter):
            fx = func(x)
            dfx = dfunc(x)

            if np.abs(dfx) < 1e-14:
                raise ZeroDivisionError(f"Derivative too small at iteration {i}, x = {x}")

            x_new = x - fx / dfx

            if abs(x_new - x) < tol:
                return x_new, i + 1

            x = x_new

        raise RuntimeError("Maximum iterations reached without convergence.")
