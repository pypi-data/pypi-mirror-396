"""Dalfox adapter for XSS vulnerability scanning."""

import subprocess
import json
from typing import Dict, Any, List
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import create_vulnerability_dict


class DalfoxAdapter(BaseAdapter):
    """
    Dalfox adapter for XSS detection.

    Dalfox (Finder of XSS) is a powerful open-source XSS scanner and utility
    focused on automation. It has advanced features for finding XSS vulnerabilities.
    """

    @property
    def name(self) -> str:
        return "dalfox"

    @property
    def description(self) -> str:
        return "Advanced XSS scanner with intelligent payload generation"

    @property
    def required_tools(self) -> List[str]:
        return ["dalfox"]

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build dalfox command.

        Args:
            target: URL to scan for XSS
            options: Configuration dictionary with options:
                - mining_dict: Use mining dict for parameter discovery
                - skip_bav: Skip BAV (Bounce After Verification)
                - only_discovery: Only discovery phase
                - silence: Silent mode
                - worker: Number of workers (default: 100)
                - timeout: Timeout in seconds (default: 10)

        Returns:
            Command string for subprocess
        """
        cmd_parts = ["dalfox", "url", target]

        # Output format - JSON
        cmd_parts.extend(["-o", "-", "--format", "json"])

        # Mining dictionary
        if options.get("mining_dict", True):
            cmd_parts.append("--mining-dict")

        # Skip BAV (faster but less accurate)
        if options.get("skip_bav", False):
            cmd_parts.append("--skip-bav")

        # Only discovery
        if options.get("only_discovery", False):
            cmd_parts.append("--only-discovery")

        # Worker count
        worker = options.get("worker", 100)
        cmd_parts.extend(["--worker", str(worker)])

        # Timeout
        timeout = options.get("timeout", 10)
        cmd_parts.extend(["--timeout", str(timeout)])

        # Silence mode
        if options.get("silence", True):
            cmd_parts.append("--silence")

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse dalfox JSON output.

        Args:
            output: Raw command output (JSON lines)

        Returns:
            Dictionary with vulnerabilities and metadata
        """
        from datetime import datetime
        import uuid

        vulnerabilities = []

        if not output or not output.strip():
            return {"vulnerabilities": vulnerabilities, "metadata": {}}

        # Parse JSON lines
        xss_findings = []
        for line in output.strip().split("\n"):
            try:
                data = json.loads(line)

                # Check if it's a POC (Proof of Concept) finding
                if data.get("type") == "POC" or "param" in data:
                    param = data.get("param", "")
                    poc_type = data.get("poc_type", "XSS")
                    evidence_data = data.get("data", "")
                    message = data.get("message", "")

                    # Determine XSS type and severity
                    severity = "high"
                    xss_type = "Reflected XSS"

                    if "dom" in poc_type.lower():
                        xss_type = "DOM-based XSS"
                        severity = "medium"
                    elif "stored" in poc_type.lower():
                        xss_type = "Stored XSS"
                        severity = "critical"

                    vuln = create_vulnerability_dict(
                        vuln_id=str(uuid.uuid4()),
                        title=f"{xss_type} Vulnerability in '{param}' parameter",
                        description=f"Cross-Site Scripting vulnerability detected in parameter '{param}'. {message}",
                        severity=severity,
                        host="",  # Will be filled by orchestrator
                        port=None,
                        service="web",
                        detected_by="dalfox",
                        evidence={
                            "parameter": param,
                            "poc_type": poc_type,
                            "payload": evidence_data,
                            "message": message,
                        },
                        remediation="Implement proper input validation and output encoding. Use Content Security Policy (CSP) headers.",
                    )
                    vulnerabilities.append(vuln)
                    xss_findings.append(data)

            except json.JSONDecodeError:
                continue

        return {
            "vulnerabilities": vulnerabilities,
            "metadata": {
                "xss_findings_count": len(xss_findings),
                "parameters_tested": list(set([f.get("param", "") for f in xss_findings])),
            },
        }
