import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from src.core.config import PROJECT_ROOT
from src.reporting.testing.junit_parser import JUnitParser
from src.reporting.testing.run_result import RunResult
from src.reporting.testing.suite_catalog import SUITE_CATALOG
from src.reporting.testing.suite_description import SuiteDescription
from src.reporting.testing.suite_result import SuiteResult


@dataclass
class PytestRunner:
    """Runs pytest in a subprocess, so it is safe to call repeatedly from a long-running server."""
    include_live: bool = False
    timeout: float = 600
    catalog: dict[str, SuiteDescription] = field(default_factory=lambda: SUITE_CATALOG)
    parser: JUnitParser = field(default_factory=JUnitParser)

    @property
    def marker(self) -> str:
        return "live or not live" if self.include_live else "not live"

    def run(self) -> RunResult:
        command = f'pytest -m "{self.marker}"'
        start = time.monotonic()

        with tempfile.TemporaryDirectory() as directory:
            junit_path = Path(directory) / "results.xml"
            try:
                self._run_pytest(junit_path)
            except (OSError, subprocess.TimeoutExpired) as error:
                return RunResult(command, time.monotonic() - start, error=str(error))

            if not junit_path.exists():
                return RunResult(command, time.monotonic() - start, error="pytest produced no results")

            return RunResult(command, time.monotonic() - start, self._suites(self.parser.parse(junit_path)))

    def _run_pytest(self, junit_path: Path):
        subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-m", self.marker, f"--junitxml={junit_path}"],
            cwd=PROJECT_ROOT, capture_output=True, timeout=self.timeout,
        )

    def _suites(self, cases_by_module: dict) -> list[SuiteResult]:
        catalogued = [SuiteResult(module, description, cases_by_module.get(module, [])) for module, description in self.catalog.items()]
        uncatalogued = [SuiteResult(module, None, cases) for module, cases in cases_by_module.items() if module not in self.catalog]
        return catalogued + uncatalogued
