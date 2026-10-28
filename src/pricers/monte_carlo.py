from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.instruments.base_option import BaseOption
from src.greeks.greeks import GREEKS, Greeks
from src.greeks.finite_differences_greeks import FiniteDifferencesGreeks
from src.market_data.market_bumper import MarketBumper
from src.pricers.base_pricer import BasePricer
from src.process.base_process import StochasticProcess
from src.schemes.base_scheme import BaseScheme
from src.simulations.simulation_result import SimulationResult
from src.pricers.monte_carlo_price_statistics import (
    MonteCarloPriceStatistics,
    calculate_price_statistics,
)
from src.process.gbm_process import GBMProcess


class VarianceReductionTechnique(str, Enum):
    ANTITHETIC = "antithetic"
    CONTROL_VARIATE = "control_variate"
    NONE = "none"


@dataclass
class MonteCarloPricer(BasePricer):
    scheme : BaseScheme
    paths: int
    n_steps: int = 64
    seed: int = 42
    finite_differences_greeks: FiniteDifferencesGreeks = field(default_factory=lambda: FiniteDifferencesGreeks(greek_bumps_config=GreeksBumpsConfig()))
    finite_differences_bumper: MarketBumper = field(default_factory=lambda: MarketBumper(greek_bumps_config=GreeksBumpsConfig()))
    variance_reduction_technique: VarianceReductionTechnique | str | None = VarianceReductionTechnique.ANTITHETIC
    

    def __post_init__(self):
        # Validate paths
        if not isinstance(self.paths, int) or self.paths <= 0:
            raise ValueError("Paths must be a positive integer greater than 0")
        
        # Validate seed
        if self.seed is None or not isinstance(self.seed, (int, np.integer)) or self.seed < 0:
            raise ValueError("Seed must be a non-negative integer")
        
        # Validate n_steps
        if not isinstance(self.n_steps, int) or self.n_steps <= 0:
            raise ValueError("n_steps must be a positive integer greater than 0")

        if self.variance_reduction_technique is None:
            self.variance_reduction_technique = VarianceReductionTechnique.NONE
        else:
            try:
                self.variance_reduction_technique = VarianceReductionTechnique(
                    self.variance_reduction_technique
                )
            except (TypeError, ValueError) as error:
                choices = ", ".join(technique.value for technique in VarianceReductionTechnique)
                raise ValueError(
                    f"variance_reduction_technique must be one of: {choices}"
                ) from error
        
        # Validate finite_differences_greeks
        if not isinstance(self.finite_differences_greeks, FiniteDifferencesGreeks):
            raise TypeError("finite_differences_greeks must be an instance of FiniteDifferencesGreeks")
        
        if not isinstance(self.scheme, BaseScheme):
            raise TypeError("Not a scheme")

        # Validate finite_differences_bumper
        if not isinstance(self.finite_differences_bumper, MarketBumper):
            raise TypeError("finite_differences_bumper must be an instance of MarketBumper")
        
        self.rng = np.random.default_rng(self.seed)
        

    
    def simulate(
        self,
        option: BaseOption,
        process: StochasticProcess,
        spot: float,
        Z: np.ndarray | None = None,
    ) -> SimulationResult:
        """Simulate terminal prices without applying variance reduction."""
        if not np.isfinite(spot) or spot <= 0:
            raise ValueError("spot must be finite and positive")

        dt = option.maturity / self.n_steps

        if Z is None:
            Z = self.rng.normal(
                0.0, 1.0, size=(self.paths, self.n_steps)
            )
        else:
            Z = np.asarray(Z, dtype=float)
            if Z.shape != (self.paths, self.n_steps):
                raise ValueError(
                    f"Z must have shape {(self.paths, self.n_steps)}"
                )
            if not np.all(np.isfinite(Z)):
                raise ValueError("Z must contain only finite values")

        brownian_increment = Z * np.sqrt(dt)
        S = np.full(self.paths, spot, dtype=float)

        for t in range(self.n_steps):
            S = self.scheme.step(
                process=process,
                price=S,
                t=dt * t,
                K=option.strike,
                dt=dt,
                brownian_increment=brownian_increment[:, t],
            )

        return SimulationResult(S, Z, dt)

    def _discounted_payoffs(
        self,
        option: BaseOption,
        process: StochasticProcess,
        terminal_paths: np.ndarray,
    ) -> np.ndarray:
        payoffs = np.asarray(
            option.payoff(terminal_paths), dtype=float
        )
        return payoffs * process.discount_factor(option.maturity)

    def _control_variate_observations(
        self,
        option: BaseOption,
        process: StochasticProcess,
        spot: float,
        terminal_paths: np.ndarray,
    ) -> np.ndarray:
        """Adjust discounted payoffs using the discounted stock price."""
        if not isinstance(process, GBMProcess):
            raise ValueError(
                "The stock-price control variate is currently supported "
                "only for GBMProcess."
            )

        y = self._discounted_payoffs(
            option, process, terminal_paths
        )
        discount = process.discount_factor(option.maturity)

        c = discount * terminal_paths
        expected_c = spot * np.exp(-process.q * option.maturity)

        if np.var(c, ddof=1) == 0:
            return y

        beta = np.cov(y, c, ddof=1)[0, 1] / np.var(c, ddof=1)
        return y - beta * (c - expected_c)

    def _estimator_observations(
        self,
        option: BaseOption,
        process: StochasticProcess,
        spot: float,
        Z: np.ndarray | None = None,
    ) -> np.ndarray:
        if Z is None:
            Z = self.rng.normal(
                0.0, 1.0, size=(self.paths, self.n_steps)
            )
        else:
            Z = np.asarray(Z, dtype=float)
            if Z.shape != (self.paths, self.n_steps):
                raise ValueError(
                    f"Z must have shape {(self.paths, self.n_steps)}"
                )

        positive = self.simulate(option, process, spot, Z)
        y = self._discounted_payoffs(
            option, process, positive.terminal_paths
        )

        if self.variance_reduction_technique == (
            VarianceReductionTechnique.ANTITHETIC
        ):
            negative = self.simulate(option, process, spot, -Z)
            y_negative = self._discounted_payoffs(
                option, process, negative.terminal_paths
            )

            return (y + y_negative) / 2.0

        if self.variance_reduction_technique == (
            VarianceReductionTechnique.CONTROL_VARIATE
        ):
            return self._control_variate_observations(
                option, process, spot, positive.terminal_paths
            )

        return y

    def price_with_statistics(
        self,
        option: BaseOption,
        process: StochasticProcess,
        spot: float,
        Z: np.ndarray | None = None,
        confidence_level: float = 0.95,
    ) -> MonteCarloPriceStatistics:
        observations = self._estimator_observations(
            option, process, spot, Z
        )
        return calculate_price_statistics(
            observations, confidence_level=confidence_level
        )

    def price(
        self,
        option: BaseOption,
        process: StochasticProcess,
        spot: float,
        Z: np.ndarray | None = None,
    ) -> float:
        """Preserve the existing API: return a single price estimate."""
        return self.price_with_statistics(
            option, process, spot, Z
        ).price


    def _discounted_payoff(self, option: BaseOption, process: StochasticProcess, simulation_result: SimulationResult, spot):
        payoffs = option.payoff(simulation_result.terminal_paths)
        discounted_price = np.mean(payoffs) * process.discount_factor(option.maturity)
        return discounted_price

    

    