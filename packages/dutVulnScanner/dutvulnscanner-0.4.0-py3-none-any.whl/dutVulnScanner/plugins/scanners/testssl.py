"""TestSSL adapter for TLS/SSL security testing."""

import subprocess
import json
from typing import Dict, Any, List
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import create_vulnerability_dict


class TestSSLAdapter(BaseAdapter):
    """
    TestSSL adapter for comprehensive TLS/SSL testing.

    testssl.sh checks a server's service on any port for the support of TLS/SSL
    ciphers, protocols as well as recent cryptographic flaws and more.
    """

    @property
    def name(self) -> str:
        return "testssl"

    @property
    def description(self) -> str:
        return "TLS/SSL security scanner for cipher and protocol testing"

    @property
    def required_tools(self) -> List[str]:
        return ["testssl.sh"]

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build testssl.sh command.

        Args:
            target: Host:port to test (e.g., "example.com:443")
            options: Configuration dictionary with options:
                - severity: Severity level for findings (default: "OK")
                - protocols: Check specific protocols
                - vulnerabilities: Check for known vulnerabilities
                - ciphers: Test cipher suites
                - server_defaults: Check server defaults
                - server_preference: Check server cipher preference

        Returns:
            Command string for subprocess
        """
        cmd_parts = ["testssl.sh"]

        # Output format - JSON
        cmd_parts.extend(["--jsonfile-pretty", "-"])

        # Check vulnerabilities by default
        if options.get("vulnerabilities", True):
            cmd_parts.append("--vulnerable")

        # Check protocols
        if options.get("protocols", True):
            cmd_parts.append("--protocols")

        # Check ciphers
        if options.get("ciphers", True):
            cmd_parts.append("--each-cipher")

        # Check server defaults
        if options.get("server_defaults", True):
            cmd_parts.append("--server-defaults")

        # Check server preference
        if options.get("server_preference", True):
            cmd_parts.append("--server-preference")

        # Severity level
        severity = options.get("severity", "OK")
        cmd_parts.extend(["--severity", severity])

        # Target
        cmd_parts.append(target)

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse testssl.sh JSON output.

        Args:
            output: Raw command output (JSON)

        Returns:
            Dictionary with vulnerabilities and metadata
        """
        from datetime import datetime
        import uuid

        vulnerabilities = []

        if not output or not output.strip():
            return {"vulnerabilities": vulnerabilities, "metadata": {}}

        try:
            data = json.loads(output)

            # Parse findings
            if isinstance(data, list):
                for finding in data:
                    severity_str = finding.get("severity", "OK").lower()

                    # Map testssl severity to our severity levels
                    severity_map = {
                        "critical": "critical",
                        "high": "high",
                        "medium": "medium",
                        "low": "low",
                        "warn": "low",
                        "info": "info",
                        "ok": "info",
                    }
                    severity = severity_map.get(severity_str, "info")

                    # Only report issues (not OK findings)
                    if severity_str not in ["ok", "info"]:
                        vuln = create_vulnerability_dict(
                            vuln_id=str(uuid.uuid4()),
                            title=finding.get("id", "SSL/TLS Issue"),
                            description=finding.get("finding", "SSL/TLS configuration issue detected"),
                            severity=severity,
                            host="",  # Will be filled by orchestrator
                            port=443,
                            service="https",
                            detected_by="testssl",
                            evidence={
                                "severity": severity_str,
                                "cve": finding.get("cve", ""),
                                "cwe": finding.get("cwe", ""),
                                "hint": finding.get("hint", ""),
                            },
                            remediation=finding.get(
                                "hint", "Review SSL/TLS configuration and update to secure protocols and ciphers."
                            ),
                        )
                        vulnerabilities.append(vuln)

        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract key issues from text
            pass

        return {"vulnerabilities": vulnerabilities, "metadata": {"ssl_issues_count": len(vulnerabilities)}}
