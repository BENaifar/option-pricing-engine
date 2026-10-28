from dataclasses import dataclass, field

from src.reporting.testing.case_result import CaseOutcome
from src.reporting.testing.suite_result import SuiteResult


@dataclass(frozen=True)
class RunResult:
    command: str
    duration: float
    suites: list[SuiteResult] = field(default_factory=list)
    error: str | None = None

    @property
    def total(self) -> int:
        return sum(len(suite.cases) for suite in self.suites)

    def count(self, outcome: CaseOutcome) -> int:
        return sum(suite.count(outcome) for suite in self.suites)
