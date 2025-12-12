from dataclasses import dataclass

from integrityguard.domain.severity import Severity


@dataclass
class ScanResult:
    """
    Represents the outcome of a single vulnerability check.
    """

    check_id: str
    check_name: str
    is_vulnerable: bool
    severity: Severity
    description: str
    evidence: str
    recommendation: str = "No Recommendations"
    trace: list[str] = None

    def __post_init__(self):
        if self.trace is None:
            self.trace = []
