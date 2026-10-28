from dataclasses import dataclass, field

from src.instruments.option_types import OptionType
from src.pipeline.pricing_pipeline import ExerciseStyle, PricerName, PricingSettings


@dataclass(frozen=True)
class OptionReportRequest:
    ticker: str
    strike: float
    maturity: float
    option_type: OptionType
    style: ExerciseStyle = ExerciseStyle.EUROPEAN
    pricers: list[PricerName] | None = None
    settings: PricingSettings = field(default_factory=PricingSettings)
    run_tests: bool = True
