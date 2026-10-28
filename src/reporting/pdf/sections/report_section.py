from abc import ABC, abstractmethod

from reportlab.platypus import Flowable

from src.reporting.report_data import ReportData


class ReportSection(ABC):
    starts_on_new_page: bool = False
    keep_together: bool = False

    @abstractmethod
    def build(self, data: ReportData) -> list[Flowable]:
        pass
