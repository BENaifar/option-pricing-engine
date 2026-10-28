from dataclasses import dataclass


@dataclass(frozen=True)
class SuiteDescription:
    title: str
    what: str
    how: str
