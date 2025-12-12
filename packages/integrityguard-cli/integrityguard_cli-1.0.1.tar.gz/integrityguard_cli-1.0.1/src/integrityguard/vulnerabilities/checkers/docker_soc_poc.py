from os import path
from uuid import uuid4

from docker import from_env
from docker.errors import DockerException

from integrityguard.domain.scan_result import ScanResult
from integrityguard.domain.severity import Severity
from integrityguard.interfaces.vulnerability_check import VulnerabilityCheck


class DockerSockPoC(VulnerabilityCheck):
    """
    Simulates writing to host filesystem to prove Data Tampering risk.
    """

    ID = "DX-002"
    NAME = "Docker Socket Host Write PoC"

    def __init__(self, cleanup: bool = True):
        self.cleanup = cleanup

    def _get_safe_result(self, trace: list[str] = None) -> ScanResult:
        if trace is None:
            trace = ["Safe result generated."]
        else:
            trace.append("Safe result generated.")

        return ScanResult(
            check_id=self.ID,
            check_name=self.NAME,
            is_vulnerable=False,
            severity=Severity.LOW,
            description="Verifies if a container can modify host files.",
            evidence="Write attempt failed or container runtime unreachable.",
            trace=trace,
        )

    def execute(self) -> ScanResult:
        trace = []
        test_filename = f"integrity_guard_{uuid4().hex}.test"
        host_path = "/etc"
        file_path = path.join(host_path, test_filename)

        trace.append(f"Generated test filename: {test_filename}")
        trace.append(f"Target host path: {host_path}")

        try:
            trace.append("Connecting to Docker client...")
            client = from_env()

            write_cmd = f"sh -c 'echo PoC > /mnt/host_tmp/{test_filename}'"
            trace.append("Attempting to run alpine container with mounted volume...")
            trace.append(
                f"Command: docker run --rm -v {host_path}:/mnt/host_tmp:rw alpine {write_cmd}"
            )

            client.containers.run(
                image="alpine",
                command=write_cmd,
                remove=True,
                volumes={host_path: {"bind": "/mnt/host_tmp", "mode": "rw"}},
            )
            trace.append("Container execution completed.")

            if not path.exists(file_path):
                trace.append("File was not created on host. Check failed or blocked.")
                return self._get_safe_result(trace)

            trace.append("File successfully created on host.")

            if self.cleanup:
                trace.append("Cleanup enabled. Removing test file...")
                cleanup_cmd = f"sh -c 'rm /mnt/host_tmp/{test_filename}'"
                trace.append(
                    f"Command: docker run --rm -v {host_path}:/mnt/host_tmp:rw alpine {cleanup_cmd}"
                )

                client.containers.run(
                    image="alpine",
                    command=cleanup_cmd,
                    remove=True,
                    volumes={host_path: {"bind": "/mnt/host_tmp", "mode": "rw"}},
                )
                trace.append("Cleanup completed.")

            return ScanResult(
                check_id=self.ID,
                check_name=self.NAME,
                is_vulnerable=True,
                severity=Severity.CRITICAL,
                description="Verifies if a container can modify host files (Data Tampering).",
                evidence=f"Successfully wrote file to host {host_path} via container volume.",
                recommendation="Use <a href='https://docs.docker.com/engine/security/rootless/' target='_blank' rel='noopener noreferrer'>Rootless Docker</a> or ensure Docker socket is not exposed.",
                trace=trace,
            )

        except (DockerException, Exception) as e:
            trace.append(f"Exception occurred: {str(e)}")
            return ScanResult(
                self.ID, self.NAME, False, Severity.INFO, "Docker daemon unreachable", str(e), "Ensure Docker is running and accessible."
            )