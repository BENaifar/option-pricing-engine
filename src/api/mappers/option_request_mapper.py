from datetime import date

from src.api.schemas import PriceRequest
from src.core.exceptions import InvalidOptionRequestError
from src.pipeline.pricing_pipeline import PricingSettings

DAYS_PER_YEAR = 365.0


def maturity_from_request(request: PriceRequest, today: date | None = None) -> float:
    if request.maturity is not None:
        return request.maturity

    days = (request.expiry - (today or date.today())).days
    if days <= 0:
        raise InvalidOptionRequestError(f"Expiry {request.expiry} must be in the future.")
    return days / DAYS_PER_YEAR


def pricing_settings_from_request(request: PriceRequest) -> PricingSettings:
    return PricingSettings(
        tree_steps=request.tree_steps,
        mc_paths=request.mc_paths,
        mc_steps=request.mc_steps,
        mc_scheme=request.mc_scheme,
        mc_variance_reduction=request.mc_variance_reduction,
        mc_confidence_level=request.mc_confidence_level,
        seed=request.seed,
    )
