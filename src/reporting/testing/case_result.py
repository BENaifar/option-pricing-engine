from dataclasses import dataclass
from enum import Enum


class CaseOutcome(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class CaseResult:
    name: str
    outcome: CaseOutcome
    duration: float
    message: str | None = None
