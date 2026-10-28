from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Spacer

from src.reporting.pdf.components import NO_NUMERIC_COLUMNS, cell, data_table, heading, key_value_table, subheading, text
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.pdf.theme import Palette
from src.reporting.report_data import ReportData
from src.reporting.testing.case_result import CaseOutcome
from src.reporting.testing.run_result import RunResult
from src.reporting.testing.suite_result import SuiteResult

INTRODUCTION = (
    "The engine is covered by an automated pytest suite, run while generating this report. Offline tests use flat "
    "synthetic markets and a fake market data provider, so they are deterministic and need no network; the live "
    "comparison against Yahoo Finance is the previous section."
)


class AutomatedTestsSection(ReportSection):
    starts_on_new_page = True

    def build(self, data: ReportData) -> list[Flowable]:
        intro = [heading("Tests"), text(INTRODUCTION)]
        tests = data.tests

        if tests is None:
            return intro + [text("Test run skipped for this report.")]
        if tests.error:
            return intro + [text(f"<b>Test run failed to start:</b> {tests.error}")]

        return intro + [
            self._totals_table(tests),
            Spacer(1, 3 * mm),
            self._suites_table(tests.suites),
            *self._failures(tests.suites),
        ]

    @staticmethod
    def _totals_table(tests: RunResult) -> Flowable:
        results = (f"{tests.count(CaseOutcome.PASSED)} passed, {tests.count(CaseOutcome.FAILED)} failed, "
                   f"{tests.count(CaseOutcome.SKIPPED)} skipped, out of {tests.total}")
        return key_value_table([("Command", tests.command), ("Duration", f"{tests.duration:.1f} s"), ("Results", results)], key_fraction=0.2)

    @staticmethod
    def _suites_table(suites: list[SuiteResult]) -> Flowable:
        rows = [["Suite", "What it checks", "How", "Tests", "Pass", "Fail"]]
        highlights = []

        for row, suite in enumerate(suites, start=1):
            description = suite.description
            failed = suite.count(CaseOutcome.FAILED)
            rows.append([
                cell(suite.title, bold=True),
                cell(description.what if description else "-"),
                cell(description.how if description else "-"),
                str(len(suite.cases)), str(suite.count(CaseOutcome.PASSED)), str(failed),
            ])
            if failed:
                highlights.append(("BACKGROUND", (-1, row), (-1, row), Palette.BAD_BACKGROUND))
            elif suite.cases:
                highlights.append(("TEXTCOLOR", (-2, row), (-2, row), Palette.GOOD))

        return data_table(rows, [0.17, 0.3, 0.35, 0.06, 0.06, 0.06], numeric_from=3, highlights=highlights)

    @staticmethod
    def _failures(suites: list[SuiteResult]) -> list[Flowable]:
        rows = [[cell(f"{suite.module}::{case.name}", bold=True), cell(case.message or "-")] for suite in suites for case in suite.failures()]
        if not rows:
            return []
        return [subheading("Failures"), data_table([["Test", "Message"]] + rows, [0.4, 0.6], numeric_from=NO_NUMERIC_COLUMNS)]
