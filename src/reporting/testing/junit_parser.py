import xml.etree.ElementTree as ElementTree
from pathlib import Path

from src.reporting.testing.case_result import CaseOutcome, CaseResult

OUTCOME_TAGS = {
    "failure": CaseOutcome.FAILED,
    "error": CaseOutcome.FAILED,
    "skipped": CaseOutcome.SKIPPED,
}
MAX_MESSAGE_LENGTH = 300


class JUnitParser:

    def parse(self, path: Path) -> dict[str, list[CaseResult]]:
        """Test cases grouped by test module, e.g. tests.test_invariants.TestInvariants -> test_invariants."""
        cases_by_module: dict[str, list[CaseResult]] = {}

        for case in ElementTree.parse(path).getroot().iter("testcase"):
            module = self._module(case.get("classname", ""))
            cases_by_module.setdefault(module, []).append(self._case(case))

        return cases_by_module

    @staticmethod
    def _module(classname: str) -> str:
        return next((part for part in classname.split(".") if part.startswith("test_")), classname)

    @staticmethod
    def _case(case: ElementTree.Element) -> CaseResult:
        name, duration = case.get("name", ""), float(case.get("time", 0.0))

        for tag, outcome in OUTCOME_TAGS.items():
            node = case.find(tag)
            if node is not None:
                message = (node.get("message") or "").strip()[:MAX_MESSAGE_LENGTH]
                return CaseResult(name, outcome, duration, message)

        return CaseResult(name, CaseOutcome.PASSED, duration)
