from dataclasses import dataclass, field

from src.reporting.testing.case_result import CaseOutcome, CaseResult
from src.reporting.testing.suite_description import SuiteDescription


@dataclass(frozen=True)
class SuiteResult:
    module: str
    description: SuiteDescription | None
    cases: list[CaseResult] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.description.title if self.description else self.module

    def count(self, outcome: CaseOutcome) -> int:
        return sum(case.outcome == outcome for case in self.cases)

    def failures(self) -> list[CaseResult]:
        return [case for case in self.cases if case.outcome == CaseOutcome.FAILED]
