from typing import List

from integrityguard.domain.ievi_score import IEVIScore
from integrityguard.domain.scan_result import ScanResult
from integrityguard.domain.severity import Severity


class IEVICalculator:
    """
    Service responsible for calculating the Integrity Violation Exposure Index (IEVI).
    """

    _SEVERITY_DREAD_MAP = {
        Severity.CRITICAL: (10, 10, 10, 10, 10),
        Severity.HIGH: (8, 9, 9, 8, 9),
        Severity.MEDIUM: (5, 6, 6, 5, 6),
        Severity.LOW: (2, 3, 3, 2, 3),
        Severity.INFO: (0, 1, 1, 0, 1),
    }

    def calculate(self, results: List[ScanResult]) -> IEVIScore:
        current_d, current_r, current_e, current_a, current_di = self._SEVERITY_DREAD_MAP[Severity.INFO]

        for res in results:
            d, r, e, a, di = self._SEVERITY_DREAD_MAP.get(
                res.severity, (0, 0, 0, 0, 0)
            )

            current_d = max(current_d, d)
            current_r = max(current_r, r)
            current_e = max(current_e, e)
            current_a = max(current_a, a)
            current_di = max(current_di, di)

        raw_average = (current_d + current_r + current_e + current_a + current_di) / 5
        ievi_total = raw_average * 10

        return IEVIScore(
            damage_potential=current_d,
            reproducibility=current_r,
            exploitability=current_e,
            affected_users=current_a,
            discoverability=current_di,
            total_score=ievi_total,
            risk_level=self._get_risk_label(ievi_total),
        )

    def _get_risk_label(self, score: float) -> str:
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        return "INFO"