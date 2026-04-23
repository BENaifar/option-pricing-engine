from dataclasses import dataclass, replace

from src.greeks.greeks_bumps_config import GreeksBumpsConfig

@dataclass
class FiniteDifferencesGreeks:
    greek_bumps_config: GreeksBumpsConfig
        
    def rho(self, price_rate_up, price_rate_down):
        return (price_rate_up - price_rate_down) / (self.greek_bumps_config.rate_abs * 2)

    def vega(self, price_vol_incr, price_vol_decr):
        return (price_vol_incr - price_vol_decr) / (self.greek_bumps_config.vol_abs * 2)

    def theta(self, dt, price_short, price_long):
        return -(price_long - price_short) / (2 * dt)

    def gamma(self, market_data, base_price, price_up, price_down):
        return (price_up - 2 * base_price + price_down) / ((self.greek_bumps_config.spot_rel * market_data.spot) ** 2)

    def delta(self, market_data, price_up, price_down):
        return (price_up - price_down) / (self.greek_bumps_config.spot_rel * market_data.spot * 2)
