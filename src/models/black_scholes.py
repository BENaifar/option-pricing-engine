import numpy as np
from scipy.stats import norm

from src.models.base_model import BaseModel

class BlackScholes(BaseModel):

    def _d1_d2(self, option, market):
        d1 = (np.log(market.spot / option.strike) + (market.risk_free_rate + 0.5 * market.sigma ** 2) * option.maturity) / (market.sigma * np.sqrt(option.maturity))
        d2 = d1 - market.sigma * np.sqrt(option.maturity)

        return d1, d2

    def supports_analytical_greeks(self):
        return True

    def price(self, option, market) -> (np.float64):
        d1, d2 = self._d1_d2(option, market)

        if (option.option_type == "call"):
            price = market.spot * norm.cdf(d1) - option.strike * np.exp((-market.risk_free_rate) * option.maturity) * norm.cdf(d2)
            return price
        else:
            price = option.strike * np.exp((-market.risk_free_rate) * option.maturity) * norm.cdf(-d2) - market.spot * norm.cdf(-d1)
            return price
        
    def delta(self, option, market):
        d1, _ = self._d1_d2(option, market)

        if (option.option_type == "call"):
            return norm.cdf(d1)
        
        else:
            return norm.cdf(d1) - 1
    
    def gamma(self, option, market):
        d1, _ = self._d1_d2(option, market)

        return norm.pdf(d1) / (
            market.spot * market.sigma * np.sqrt(option.maturity)
        )
    
    def vega(self, option, market):
        d1, _ = self._d1_d2(option, market)

        return market.spot * norm.pdf(d1) * np.sqrt(option.maturity)
    
    def theta(self, option, market):
        d1, d2 = self._d1_d2(option, market)
        spot = market.spot
        strike = option.strike
        maturity = option.maturity
        sigma = market.sigma
        risk_free_rate = market.risk_free_rate

        volatility_decay = - ((spot * norm.pdf(d1) * sigma)
                   / (2 * np.sqrt(maturity)))
        
        if (option.option_type == 'call'):
            theta = volatility_decay - risk_free_rate * strike * np.exp((-risk_free_rate) * maturity) * norm.cdf(d2)
            return theta

        else:
            theta = volatility_decay + risk_free_rate * strike * np.exp((-risk_free_rate) * maturity) * norm.cdf(-d2)
            return theta
        
    def rho(self, option, market):
        _, d2 = self._d1_d2(option, market)
        strike = option.strike
        maturity = option.maturity
        risk_free_rate = market.risk_free_rate

        if (option.option_type == "call"):
            return strike * maturity * np.exp(-risk_free_rate * maturity) * norm.cdf(d2)
        
        else:
            return -strike * maturity * np.exp(-risk_free_rate * maturity) * norm.cdf(-d2)