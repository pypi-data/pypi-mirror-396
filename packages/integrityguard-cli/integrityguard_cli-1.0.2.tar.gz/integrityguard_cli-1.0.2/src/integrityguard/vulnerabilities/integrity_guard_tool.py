from dataclasses import asdict
from json import dumps
from typing import List
from logging import info

from integrityguard.domain.ievi_score import IEVIScore
from integrityguard.domain.scan_result import ScanResult
from integrityguard.interfaces.vulnerability_check import VulnerabilityCheck
from integrityguard.services.ievi_calculator import IEVICalculator
from integrityguard.services.html_report_generator import HTMLReportGenerator


class IntegrityGuardTool:
    def __init__(self, checks: List[VulnerabilityCheck] = None, output_formats: list[str] = ["json"]):
        self._checks: List[VulnerabilityCheck] = checks if checks is not None else []
        self._calculator = IEVICalculator()
        self._report_generator = HTMLReportGenerator()
        self._output_formats = output_formats

    def run_analysis(self):
        info("--- Starting IntegrityGuard Analysis ---")
        results = []

        for check in self._checks:
            result = check.execute()
            results.append(result)
            info(
                f"[*] Check {result.check_name}: {'VULNERABLE' if result.is_vulnerable else 'SAFE'}"
            )

        ievi_score = self._calculator.calculate(results)

        self._generate_report(results, ievi_score)

    def _generate_report(self, results: List[ScanResult], score: IEVIScore):

        final_report = {
            "summary": {
                "ievi_score": score.total_score,
                "risk_level": score.risk_level,
                "dread_breakdown": {
                    "D": score.damage_potential,
                    "R": score.reproducibility,
                    "E": score.exploitability,
                    "A": score.affected_users,
                    "Di": score.discoverability,
                },
            },
            "findings": [asdict(res) for res in results],
        }

        if "json" in self._output_formats:
            info("\n--- JSON Output (Ready for HTML Report) ---")
            info(dumps(final_report, indent=4, default=str))

        if "html" in self._output_formats:
            self._report_generator.generate(final_report)
