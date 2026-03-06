from src.market_data.market_data import MarketData
from src.pricers.base_pricer import BasePricer
from src.instruments.base_option import BaseOption


class EuropeanPricer(BasePricer):
    
    def price(self, option: BaseOption, market_data: MarketData) -> float:
        return float(self.model.price(option, market_data))
    
    def greeks(self, option: BaseOption, market_data: MarketData) -> dict[str, float] | None:
        if self.model.supports_analytical_greeks():
            return {
                "delta": self.model.delta(option, market_data),
                "gamme": self.model.gamma(option, market_data),
                "vega": self.model.vega(option, market_data),
                "theta": self.model.theta(option, market_data),
                "rho": self.model.rho(option, market_data)
            }
        else:
            raise NotImplementedError("No analytical Greeks implemented")
            