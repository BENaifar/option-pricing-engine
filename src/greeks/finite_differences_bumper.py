from dataclasses import dataclass, replace

from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.instruments.base_option import BaseOption
from src.market_data.market_data import MarketData

@dataclass
class FiniteDifferencesBumper:
    greek_bumps_config: GreeksBumpsConfig

    def bump_spot(self, market_data: MarketData):

        market_down = replace(market_data, spot=(market_data.spot * (1 - self.greek_bumps_config.spot_rel)))
        market_up = replace(market_data, spot=(market_data.spot * (1 + self.greek_bumps_config.spot_rel)))

        return market_down, market_up
    
    def bump_time(self, option: BaseOption):
        dt = self.greek_bumps_config.time_days

        shorter_maturity = max(option.maturity - dt, 1e-8)
        longer_maturity = max(option.maturity + dt, 2e-8)

        option_short = replace(option, maturity=shorter_maturity)
        option_long = replace(option, maturity=longer_maturity)
        
        return dt, option_short, option_long
    
    def bump_volatility(self, market_data: MarketData):
        volatility_up = replace(market_data, sigma=(market_data.sigma + self.greek_bumps_config.vol_abs))
        volatility_down = replace(market_data, sigma=(market_data.sigma - self.greek_bumps_config.vol_abs))

        return volatility_up,volatility_down
    
    def bump_rate(self, market_data: MarketData):
        rate_up = replace(market_data, rate=(market_data.rate + self.greek_bumps_config.rate_abs))
        rate_down = replace(market_data, rate=(market_data.rate - self.greek_bumps_config.rate_abs))

        return rate_up,rate_down