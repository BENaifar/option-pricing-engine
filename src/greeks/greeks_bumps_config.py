from dataclasses import dataclass, field

@dataclass(frozen=True)
class GreeksBumpsConfig:
    spot_rel: float = 0.01
    vol_abs: float = 0.01
    rate_abs: float = 1e-4
    time_days: float = 1/365

