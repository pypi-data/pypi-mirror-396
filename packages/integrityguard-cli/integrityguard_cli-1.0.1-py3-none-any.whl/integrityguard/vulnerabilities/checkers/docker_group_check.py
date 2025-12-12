from grp import getgrall
from os import getenv

from integrityguard.domain.scan_result import ScanResult
from integrityguard.domain.severity import Severity
from integrityguard.interfaces.vulnerability_check import VulnerabilityCheck


class DockerGroupCheck(VulnerabilityCheck):
    """
    Checks if current user is in 'docker' group.
    """

    ID = "DX-001"
    NAME = "User Docker Group Membership"

    def execute(self) -> ScanResult:
        trace = []
        user = getenv("USER")
        trace.append(f"Identified current user: {user}")

        is_member = False
        evidence = "User is not in docker group."

        try:
            trace.append("Retrieving all groups and their members...")
            groups = [g.gr_name for g in getgrall() if user in g.gr_mem]
            trace.append(f"User belongs to groups: {', '.join(groups)}")

            if "docker" in groups:
                trace.append("Found 'docker' in user's group list.")
                is_member = True
                evidence = f"User '{user}' found in 'docker' group."
            else:
                trace.append("'docker' group not found in user's group list.")

        except Exception as e:
            error_msg = f"Error checking groups: {str(e)}"
            trace.append(error_msg)
            evidence = error_msg

        return ScanResult(
            check_id=self.ID,
            check_name=self.NAME,
            is_vulnerable=is_member,
            severity=Severity.CRITICAL if is_member else Severity.LOW,
            description="Checks if the user has root-equivalent access via docker group.",
            evidence=evidence,
            recommendation=(
                "Remove the user from the 'docker' group to prevent root privilege escalation."
                if is_member
                else "No Recommendations"
            ),
            trace=trace,
        )
