from dataclasses import dataclass

from src.core.config import read_config_float

@dataclass(frozen=True)
class GreeksBumpsConfig:

    spot_rel: float = read_config_float('greek_bumps', 'spot_rel')
    gamma_rel: float = read_config_float('greek_bumps', 'gamma_rel')
    vol_abs: float = read_config_float('greek_bumps', 'vol_abs')
    rate_abs: float = read_config_float('greek_bumps', 'rate_abs')
    time_days: float = read_config_float('greek_bumps', 'time_days')

