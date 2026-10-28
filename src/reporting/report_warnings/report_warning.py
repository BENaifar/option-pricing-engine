from dataclasses import dataclass


@dataclass(frozen=True)
class ReportWarning:
    title: str
    message: str
