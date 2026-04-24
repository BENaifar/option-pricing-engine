from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.instruments.base_option import BaseOption
from src.greeks.greeks import GREEKS, Greeks
from src.greeks.finite_differences_greeks import FiniteDifferencesGreeks
from src.market_data.market_bumper import MarketBumper
from src.models.base_model import BaseModel
from src.pricers.base_pricer import BasePricer
from src.numerics.base_scheme import BaseScheme
from src.market_data.market_data import MarketData
from src.simulations.simulation_result import SimulationResult

@dataclass
class MonteCarloPricer(BasePricer):
    model: BaseModel
    scheme : BaseScheme
    paths: int
    n_steps: int = 64
    seed: int = 42
    finite_differences_greeks: FiniteDifferencesGreeks = field(default_factory=lambda: FiniteDifferencesGreeks(greek_bumps_config=GreeksBumpsConfig()))
    finite_differences_bumper: MarketBumper = field(default_factory=lambda: MarketBumper(greek_bumps_config=GreeksBumpsConfig()))
    

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
        
        # Validate model
        if not isinstance(self.model, BaseModel):
            raise TypeError("model must be an instance of BaseModel")
        
        # Validate scheme
        if not isinstance(self.scheme, BaseScheme):
            raise TypeError("scheme must be an instance of BaseScheme")
        
        # Validate finite_differences_greeks
        if not isinstance(self.finite_differences_greeks, FiniteDifferencesGreeks):
            raise TypeError("finite_differences_greeks must be an instance of FiniteDifferencesGreeks")
        
        # Validate finite_differences_bumper
        if not isinstance(self.finite_differences_bumper, MarketBumper):
            raise TypeError("finite_differences_bumper must be an instance of MarketBumper")
        
        self.rng = np.random.default_rng(self.seed)
        

    def simulate(self, option: BaseOption, market_data: MarketData, Z: np.ndarray | None = None) -> SimulationResult:
        dt = option.maturity / self.n_steps

        if Z is None:
            Z = self.rng.normal(0, 1, size=[self.paths, self.n_steps])
        
        brownian_increment = Z * np.sqrt(dt)
        
        S = np.full(self.paths, market_data.spot, dtype=float)

        step = self.scheme.step
        model = self.model
        n_steps = self.n_steps

        for t in range(n_steps):
            S = step(
                model,
                market_data,
                S,
                t * dt,
                dt,
                brownian_increment[:, t]
            )

        return SimulationResult(S, Z, dt)  # type: ignore
    
    def price(self, option: BaseOption, market_data: MarketData):
        simulation_result = self.simulate(option, market_data)
        return self._discounted_payoff(option, market_data, simulation_result)

    def _discounted_payoff(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult):
        payoffs = option.payoff(simulation_result.terminal_paths)
        discounted_price = np.mean(payoffs) * np.exp((-market_data.rate) * option.maturity)
        return discounted_price
    
    def _repriced_with_normals(
        self,
        option: BaseOption,
        market: MarketData,
        normals: np.ndarray
    ) -> float:
        result = self.simulate(option, market, normals)
        return self._discounted_payoff(option, market, result)
    
    def _price_from_paths(self, option: BaseOption, market_data: MarketData, paths):
        payoffs = option.payoff(paths)
        discounted_price = np.mean(payoffs) * np.exp((-market_data.rate) * option.maturity)
        return discounted_price
    
    def greeks(self, option: BaseOption, market_data: MarketData, greeks_list: list[GREEKS] | None = None) -> Greeks:
        required = self._validate_required(greeks_list=greeks_list)

        simulation_result = self.simulate(option, market_data)

        greeks_values: dict[str, Optional[float]] = {
            'delta': None,
            'gamma': None,
            'theta': None,
            'vega': None,
            'rho': None
        }

        if GREEKS.DELTA in required or GREEKS.GAMMA in required:
            greeks_values['delta'], greeks_values['gamma'] = self._spot_greeks(option, market_data, simulation_result)

        if GREEKS.THETA in required:
            greeks_values['theta'] = self._theta(option, market_data, simulation_result)
        
        if GREEKS.VEGA in required:
            greeks_values['vega'] = self._vega(option, market_data, simulation_result)

        if GREEKS.RHO in required:
            greeks_values['rho'] = self._rho(option, market_data, simulation_result)

        return Greeks(**greeks_values)

    def _rho(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult) -> float:
        rate_up, rate_down = self.finite_differences_bumper.bump_rate(market_data)

        price_rate_up = self._repriced_with_normals(option, rate_up, simulation_result.normals)
        price_rate_down = self._repriced_with_normals(option, rate_down, simulation_result.normals)

        rho = self.finite_differences_greeks.rho(price_rate_up, price_rate_down)

        return rho

    def _vega(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult) -> float:
        volatility_up, volatility_down = self.finite_differences_bumper.bump_volatility(market_data)

        price_vol_incr = self._repriced_with_normals(option, volatility_up, simulation_result.normals)
        price_vol_decr = self._repriced_with_normals(option, volatility_down, simulation_result.normals)

        vega = self.finite_differences_greeks.vega(price_vol_incr, price_vol_decr)

        return float(vega)

    def _theta(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult) -> float:
        dt, option_short, option_long = self.finite_differences_bumper.bump_time(option)

        price_short = self._repriced_with_normals(option_short, market_data, simulation_result.normals)
        price_long = self._repriced_with_normals(option_long, market_data, simulation_result.normals)

        theta = self.finite_differences_greeks.theta(dt, price_short, price_long)

        return float(theta)

    def _spot_greeks(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult) -> tuple[float, float]:
        base_price = self._price_from_paths(option, market_data, simulation_result.terminal_paths)

        market_down, market_up = self.finite_differences_bumper.bump_spot(market_data)


        price_up = self._repriced_with_normals(option, market_up, simulation_result.normals)
        price_down = self._repriced_with_normals(option, market_down, simulation_result.normals)

        delta = self.finite_differences_greeks.delta(market_data, price_up, price_down)
        gamma = self.finite_differences_greeks.gamma(market_data, base_price, price_up, price_down)

        return delta, gamma