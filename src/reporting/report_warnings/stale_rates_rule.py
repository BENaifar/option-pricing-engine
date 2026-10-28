from dataclasses import dataclass
from datetime import datetime

from src.reporting.report_data import ReportData
from src.reporting.report_warnings.report_warning import ReportWarning
from src.reporting.report_warnings.warning_rule import WarningRule


@dataclass(frozen=True)
class StaleRatesRule(WarningRule):
    max_age_days: int = 7

    def evaluate(self, data: ReportData) -> ReportWarning | None:
        as_of = getattr(data.snapshot.rate, "as_of", None)
        if as_of is None:
            return None

        valuation_date = datetime.fromisoformat(data.snapshot.timestamp).date()
        age = (valuation_date - as_of).days
        if age <= self.max_age_days:
            return None

        return ReportWarning(
            title="Stale interest rates",
            message=(
                f"The Treasury rates (FRED files in <font face='Courier'>data/raw/DGS</font>) end on "
                f"{as_of:%Y-%m-%d}, {age} days before the valuation date. Download fresh DGS series from FRED. "
                "Until then r(T) is out of date; the implied carry absorbs most of the error in forwards, "
                "but discounting stays off by roughly the rate change times maturity."
            ),
        )
