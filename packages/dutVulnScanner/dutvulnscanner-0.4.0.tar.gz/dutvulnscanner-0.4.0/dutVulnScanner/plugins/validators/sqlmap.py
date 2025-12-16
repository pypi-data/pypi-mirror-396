"""SQLMap adapter for SQL injection testing."""

import uuid
from datetime import datetime
from typing import Dict, Any
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import Vulnerability, SeverityLevel


class SqlmapAdapter(BaseAdapter):
    """Adapter for SQLMap SQL injection scanner."""

    name = "sqlmap"

    @property
    def description(self) -> str:
        return "Automated SQL injection detection and exploitation"

    @property
    def category(self) -> str:
        return "vulnerability_exploitation"

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build SQLMap command.

        Args:
            target: Target URL
            options: SQLMap options

        Returns:
            Command string
        """
        cmd_parts = ["sqlmap"]

        # Target URL
        cmd_parts.extend(["-u", target])

        # Batch mode (non-interactive)
        cmd_parts.append("--batch")

        # Risk and level
        risk = options.get("risk", 1)
        level = options.get("level", 1)
        cmd_parts.extend(["--risk", str(risk)])
        cmd_parts.extend(["--level", str(level)])

        # Technique
        technique = options.get("technique")
        if technique:
            cmd_parts.extend(["--technique", technique])

        # Database to enumerate
        if options.get("enumerate_dbs"):
            cmd_parts.append("--dbs")

        # Output format
        cmd_parts.append("--output-dir=/tmp/sqlmap-output")

        # Verbosity
        verbosity = options.get("verbosity", 1)
        cmd_parts.extend(["-v", str(verbosity)])

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse SQLMap output.

        Args:
            output: Raw SQLMap output

        Returns:
            Parsed vulnerabilities and findings
        """
        vulnerabilities = []
        findings = {"injectable_parameters": [], "databases": [], "dbms": None, "injection_types": []}

        lines = output.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Detect SQL injection
            if "Parameter:" in line and "is vulnerable" in line:
                param_name = line.split("Parameter:")[1].split("is vulnerable")[0].strip()
                findings["injectable_parameters"].append(param_name)

                vuln = Vulnerability(
                    id=str(uuid.uuid4()),
                    title=f"SQL Injection in parameter '{param_name}'",
                    description=f"SQL injection vulnerability detected in parameter: {param_name}",
                    severity=SeverityLevel.CRITICAL,
                    cvss_score=9.0,
                    host="",  # Will be set by orchestrator
                    port=None,
                    protocol=None,
                    service=None,
                    detected_by=self.name,
                    detection_time=datetime.utcnow().isoformat(),
                    evidence={"parameter": param_name, "tool_output": line},
                    remediation="Use parameterized queries or prepared statements to prevent SQL injection",
                )
                vulnerabilities.append(vuln.dict())

            # Detect DBMS
            if "back-end DBMS:" in line.lower():
                findings["dbms"] = line.split(":")[-1].strip()

            # Detect injection types
            if "Type:" in line:
                injection_type = line.split("Type:")[-1].strip()
                findings["injection_types"].append(injection_type)

        return {
            "findings": findings,
            "vulnerabilities": vulnerabilities,
            "metadata": {
                "tool": self.name,
                "category": self.category,
            },
        }

    def get_docker_image(self) -> str:
        """Get Docker image name."""
        return "pberba/sqlmap"
