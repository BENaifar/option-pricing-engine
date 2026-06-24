from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicSpline

from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.forward_price_engine import ForwardPricing
from src.market_data.models.iv_quote import IVQuote
from src.market_data.models.volatility_model import VolatilityModel

@dataclass
class VolatilitySmileBuilder(VolatilityModel):
    options: list[IVQuote]
    T: float
    spot: float
    dividend_curve: DividendCurve
    yield_curve: YieldCurve
    
    def __post_init__(self):
        self.moneyness, self.ivs = self.compute_moneyness_list()
        idx = np.argsort(self.moneyness)
        self.moneyness = self.moneyness[idx]
        self.ivs = self.ivs[idx]
        self.curve = self._get_spline()

    def compute_moneyness_list(self):
        m = []
        ivs = []

        for opt in self.options:
            moneyness = self.compute_moneyness(opt.K)
            ivs.append(opt.iv)
            m.append(moneyness)

        return np.array(m), np.array(ivs)
    
    def get_vol(self, strike: float):
        moneyness = self.compute_moneyness(strike)

        return self.curve(moneyness)

    def compute_moneyness(self, strike):
        F = ForwardPricing.forward_price(
            self.spot,
            self.yield_curve,
            self.dividend_curve,
            self.T
        )
        moneyness = np.log(strike / F)
        return moneyness


    def _get_spline(self):
        return CubicSpline(
            self.moneyness,
            self.ivs,
            bc_type="natural"
        )

        

    


    