from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.instruments.base_option import BaseOption
from src.instruments.option_types import OptionType
from src.market_data.market_data import MarketData
from src.pricers.base_pricer import BasePricer
from src.greeks.greeks import Greeks, GREEKS

@dataclass(frozen=True)
class BSTerms:
    S: float
    K: float
    sigma: float
    T: float
    r: float
    q: float
    sqrtT: float
    disc: float
    disc_q:float
    norm_pdf_d1: float | None | np.ndarray
    norm_cdf_d1: float | None | np.ndarray
    norm_cdf_d2: float | None | np.ndarray

@dataclass
class BlackScholesPricer(BasePricer):

    def _d1_d2(self, option: BaseOption, market_data: MarketData) -> tuple[float, float]:
        d1 = (np.log(market_data.spot / option.strike) + (market_data.rate - market_data.dividend_yield + 0.5 * market_data.sigma ** 2) * option.maturity) / (market_data.sigma * np.sqrt(option.maturity))
        d2 = d1 - market_data.sigma * np.sqrt(option.maturity)

        return d1, d2


    def price(self, option: BaseOption, market_data: MarketData) -> float:
        d1, d2 = self._d1_d2(option, market_data)

        if (option.option_type == OptionType.CALL):
            price = market_data.spot * np.exp(-market_data.dividend_yield * option.maturity) * norm.cdf(d1) - option.strike * np.exp((-market_data.rate) * option.maturity) * norm.cdf(d2)
            return float(price)
        elif (option.option_type == OptionType.PUT):
            price = option.strike * np.exp((-market_data.rate) * option.maturity) * norm.cdf(-d2) - market_data.spot * np.exp(-market_data.dividend_yield * option.maturity) * norm.cdf(-d1)
            return float(price)
        
        else:
            raise ValueError("The option type is not recognized")
        
    def greeks(self, option: BaseOption, market_data: MarketData, greeks_list: list | None = None) -> Greeks:

        required = self._validate_required(greeks_list)
        bs_terms = self._precompute_terms(option, market_data, required)
        return self._compute_greeks(option, required, bs_terms)

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

    def _precompute_terms(self, option: BaseOption, market_data: MarketData, required) -> BSTerms:
        d1, d2 = self._d1_d2(option, market_data)
        norm_pdf_d1 = None
        norm_cdf_d1 = None
        norm_cdf_d2 = None

        if (required & {"gamma","vega","theta"}):
            norm_pdf_d1 = norm.pdf(d1)

        if (required & {"delta"}):
            norm_cdf_d1 = norm.cdf(d1)

        if (required & {"theta", "rho"}):
            norm_cdf_d2 = norm.cdf(d2)

        S = market_data.spot
        K = option.strike
        sigma = market_data.sigma
        T = option.maturity
        r = market_data.rate
        q = market_data.dividend_yield
        sqrtT = np.sqrt(T)
        disc = np.exp(-r*T)
        disc_q = np.exp(-market_data.dividend_yield * option.maturity)

        return BSTerms(S, K, sigma, T, r, q, sqrtT, disc, disc_q, norm_pdf_d1, norm_cdf_d1, norm_cdf_d2)

    def _compute_greeks(self, option: BaseOption, required, bs_terms: BSTerms) -> Greeks:
        delta = None
        gamma = None
        theta = None
        vega = None
        rho = None
        
        if "delta" in required:            
            if option.option_type == OptionType.CALL:
                delta = float(bs_terms.norm_cdf_d1 * bs_terms.disc_q)
            else:
                delta = float((bs_terms.norm_cdf_d1 - 1) * bs_terms.disc_q)
        
        if "theta" in required:
            if option.option_type == OptionType.CALL:
                theta = float(
                    -((bs_terms.S * bs_terms.disc_q * bs_terms.norm_pdf_d1 * bs_terms.sigma) / (2 * bs_terms.sqrtT))
                    - bs_terms.r * bs_terms.K * bs_terms.disc * bs_terms.norm_cdf_d2
                    + bs_terms.q * bs_terms.S * bs_terms.disc_q * bs_terms.norm_cdf_d1
                )

            else:
                theta = float(
                    -((bs_terms.S * bs_terms.disc_q * bs_terms.norm_pdf_d1 * bs_terms.sigma) / (2 * bs_terms.sqrtT))
                    + bs_terms.r * bs_terms.K * bs_terms.disc * (1 - bs_terms.norm_cdf_d2)
                    - bs_terms.q * bs_terms.S * bs_terms.disc_q * (1 - bs_terms.norm_cdf_d1)
                )        
        if "gamma" in required:
            gamma = float((bs_terms.norm_pdf_d1 / (bs_terms.S * bs_terms.sigma * bs_terms.sqrtT)) * bs_terms.disc_q)
        
        if "vega" in required:
            vega = float(bs_terms.S * bs_terms.sqrtT * bs_terms.norm_pdf_d1 * bs_terms.disc_q)
        
        if "rho" in required:
            if option.option_type == OptionType.CALL:
                rho = float(bs_terms.K * bs_terms.T * bs_terms.disc * bs_terms.norm_cdf_d2)
            else:
                rho = -float(bs_terms.K * bs_terms.T * bs_terms.disc * (1 - bs_terms.norm_cdf_d2))

        return Greeks(
            delta=delta,
            gamma=gamma, 
            theta=theta, 
            rho=rho, 
            vega=vega
        )