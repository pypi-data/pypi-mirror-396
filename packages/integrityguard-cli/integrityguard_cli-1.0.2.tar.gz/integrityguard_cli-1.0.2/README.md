# IntegrityGuard: Docker Security Assessment Tool

[![PyPI version](https://badge.fury.io/py/integrityguard-cli.svg)](https://badge.fury.io/py/integrityguard-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**IntegrityGuard** is a security tool designed to detect **Privilege Escalation** and **Data Tampering** risks in multi-user Docker environments.

It implements the methodology described in the research *"Segurança em Docker Multiusuário: Avaliação de Riscos"*, focusing on the dangers of exposing the Docker socket (`/var/run/docker.sock`) to non-privileged users.

## 🚀 Key Features

* **Vulnerability Diagnosis:** Checks if the current user is improperly added to the `docker` group or has write access to the socket.
* **Safe Proof-of-Concept (PoC):** Simulates a "Host Breakout" attack by attempting to mount the host filesystem and write a harmless test file, proving the viability of Data Tampering without damaging the system.
* **IEVI Score Calculation:** Quantifies the risk using the **Integrity Violation Exposure Index (IEVI)**, a metric derived from the **DREAD** threat modeling framework.
* **SonarQube-like Reporting:** Generates visual HTML dashboards or JSON output for CI/CD integration.

## 📦 Installation

Install the tool directly from PyPI:

```bash
pip install integrityguard-cli
````

## 🛠️ Usage

Once installed, the `integrity-guard` command is available globally.

### 1\. Standard Analysis (Console Output)

Runs the diagnosis and prints the findings and IEVI score to the terminal.

```bash
integrity-guard
```

### 2\. Generate HTML Dashboard

Creates a visual report (`integrity_scan_report.html`) containing the risk score, DREAD breakdown, and detailed findings.

```bash
integrity-guard --html
```

### 3\. JSON Output (DevOps/CI)

Outputs the raw data in JSON format for parsing by other tools.

```bash
integrity-guard --json
```

## 📊 How It Works (Methodology)

The tool operates in three phases:

1.  **Diagnosis:** It inspects user permissions and group memberships. Adding a user to the `docker` group is equivalent to granting them `root` access.
2.  **Simulation:** It attempts to spin up a container with `-v /:/mnt/host` to verify if the host filesystem is writable.
3.  **Scoring:** It calculates the **IEVI** (Integrity Violation Exposure Index).
      * **Score \> 40:** Indicates a **Critical** risk where an attacker can modify `/etc/passwd` or other sensitive files.
      * **Score \< 40:** Indicates a **Tolerable** risk (e.g., Rootless Docker).

## 🛡️ Mitigation

If **IntegrityGuard** reports a critical vulnerability, the recommended mitigation is to migrate to **Docker Rootless** mode or remove the user from the `docker` group.

## 📝 License

This project is licensed under the MIT License.