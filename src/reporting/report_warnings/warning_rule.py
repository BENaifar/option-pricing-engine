from abc import ABC, abstractmethod

from src.reporting.report_data import ReportData
from src.reporting.report_warnings.report_warning import ReportWarning


class WarningRule(ABC):

    @abstractmethod
    def evaluate(self, data: ReportData) -> ReportWarning | None:
        pass
