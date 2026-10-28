import math

from src.pipeline.pricing_pipeline import PricerName

MISSING = "-"

PRICER_LABELS = {
    PricerName.CLOSED_BLACK_SCHOLES: "Closed-form Black-Scholes",
    PricerName.BINOMIAL_TREE: "Binomial tree (CRR)",
    PricerName.MONTE_CARLO: "Monte Carlo",
}


def _is_missing(value: float | None) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def number(value: float | None, digits: int = 4) -> str:
    return MISSING if _is_missing(value) else f"{value:,.{digits}f}"


def _without_negative_zero(value: float, digits: int) -> float:
    return round(value, digits) or 0.0


def signed(value: float | None, digits: int = 3) -> str:
    return MISSING if _is_missing(value) else f"{_without_negative_zero(value, digits):+.{digits}f}"


def percent(value: float | None, digits: int = 2) -> str:
    return MISSING if _is_missing(value) else f"{value:.{digits}%}"


def signed_percent(value: float | None, digits: int = 2) -> str:
    return MISSING if _is_missing(value) else f"{_without_negative_zero(value, digits + 2):+.{digits}%}"
