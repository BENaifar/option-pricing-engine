from dataclasses import dataclass, replace

import numpy as np
from typing import Dict, Optional

from src.instruments.base_option import BaseOption
from src.greeks.greeks import GREEKS, Greeks
from src.greeks.greeks_bumps_config import GreeksBumpsConfig
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
    seed: int
    greek_bumps_config: GreeksBumpsConfig
    n_steps: int = 64

    def __post_init__(self):
        if self.paths <= 0 or not isinstance(self.paths, (int, np.integer)):
            raise ValueError("Paths can only be positive and over 0")
        if self.seed is None or self.seed < 0 or not isinstance(self.seed, (int, np.integer)):
            raise ValueError("Seed must be provided")
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
    
    def greeks(self, option: BaseOption, market_data: MarketData, greeks_list: list[GREEKS] | None) -> Greeks:
        required = self._validate_required(greeks_list=greeks_list)

        simulation_result = self.simulate(option, market_data)

        greeks_values: Dict[str, Optional[float]] = {
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
        rate_up = replace(market_data, rate=(market_data.rate + self.greek_bumps_config.rate_abs))
        rate_down = replace(market_data, rate=(market_data.rate - self.greek_bumps_config.rate_abs))

        price_rate_up = self._repriced_with_normals(option, rate_up, simulation_result.normals)
        price_rate_down = self._repriced_with_normals(option, rate_down, simulation_result.normals)

        rho = (price_rate_up - price_rate_down) / (self.greek_bumps_config.rate_abs * 2)

        return rho

    def _vega(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult) -> float:
        volatility_up = replace(market_data, sigma=(market_data.sigma + self.greek_bumps_config.vol_abs))
        volatility_down = replace(market_data, sigma=(market_data.sigma - self.greek_bumps_config.vol_abs))

        price_vol_incr = self._repriced_with_normals(option, volatility_up, simulation_result.normals)
        price_vol_decr = self._repriced_with_normals(option, volatility_down, simulation_result.normals)

        vega = (price_vol_incr - price_vol_decr) / (self.greek_bumps_config.vol_abs * 2)

        return float(vega)

    def _theta(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult) -> float:
        dt = self.greek_bumps_config.time_days

        shorter_maturity = max(option.maturity - dt, 1e-8)
        longer_maturity = max(option.maturity + dt, 2e-8)

        option_short = replace(option, maturity=shorter_maturity)
        option_long = replace(option, maturity=longer_maturity)

        price_short = self._repriced_with_normals(option_short, market_data, simulation_result.normals)
        price_long = self._repriced_with_normals(option_long, market_data, simulation_result.normals)

        theta = -(price_long - price_short) / (2 * dt)

        return float(theta)

    def _spot_greeks(self, option: BaseOption, market_data: MarketData, simulation_result: SimulationResult) -> tuple[float, float]:
        base_price = self._price_from_paths(option, market_data, simulation_result.terminal_paths)

        market_down = replace(market_data, spot=(market_data.spot * (1 - self.greek_bumps_config.spot_rel)))
        market_up = replace(market_data, spot=(market_data.spot * (1 + self.greek_bumps_config.spot_rel)))

        price_up = self._repriced_with_normals(option, market_up, simulation_result.normals)
        price_down = self._repriced_with_normals(option, market_down, simulation_result.normals)

        delta = (price_up - price_down) / (self.greek_bumps_config.spot_rel * market_data.spot * 2)
        gamma = (price_up - 2 * base_price + price_down) / ((self.greek_bumps_config.spot_rel * market_data.spot) ** 2)

        return delta, gamma


    def _validate_required(self, greeks_list):
        if greeks_list is None:
            greeks_list = [GREEKS.DELTA, GREEKS.GAMMA, GREEKS.THETA, GREEKS.RHO, GREEKS.VEGA]
        
        if not isinstance(greeks_list, list):
            raise TypeError(f"greeks_list must be a list or None, got {type(greeks_list).__name__}")
        
        for greek in greeks_list:
            if not isinstance(greek, GREEKS):
                raise ValueError(f"Invalid greek: {greek}. Must be one of {[g.name for g in GREEKS]}")
        
        required = set(g.value for g in greeks_list)
        return required        