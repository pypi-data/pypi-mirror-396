"""Subfinder adapter for subdomain enumeration."""

import subprocess
import json
from typing import Dict, Any, List
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import Vulnerability


class SubfinderAdapter(BaseAdapter):
    """
    Subfinder adapter for fast subdomain discovery.

    Subfinder is a subdomain discovery tool that discovers valid subdomains
    using passive sources. It's faster and cleaner than Amass for pipeline usage.
    """

    @property
    def name(self) -> str:
        return "subfinder"

    @property
    def description(self) -> str:
        return "Fast subdomain enumeration using passive sources"

    @property
    def required_tools(self) -> List[str]:
        return ["subfinder"]

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build subfinder command.

        Args:
            target: Domain to enumerate
            options: Configuration dictionary with options:
                - all: Use all sources (default: true)
                - recursive: Enable recursive subdomain discovery
                - timeout: Timeout in seconds (default: 30)
                - max_time: Maximum enumeration time (default: 10)
                - threads: Number of concurrent threads (default: 10)

        Returns:
            Command string for subprocess
        """
        cmd_parts = ["subfinder", "-d", target, "-json"]

        # Use all sources by default
        if options.get("all", True):
            cmd_parts.append("-all")

        # Recursive discovery
        if options.get("recursive", False):
            cmd_parts.append("-recursive")

        # Timeout settings
        timeout = options.get("timeout", 30)
        cmd_parts.extend(["-timeout", str(timeout)])

        max_time = options.get("max_time", 10)
        cmd_parts.extend(["-max-time", str(max_time)])

        # Threading
        threads = options.get("threads", 10)
        cmd_parts.extend(["-t", str(threads)])

        # Silent mode for clean JSON output
        cmd_parts.append("-silent")

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse subfinder JSON output.

        Args:
            output: Raw command output (JSON lines)

        Returns:
            Dictionary with vulnerabilities and metadata
        """
        from datetime import datetime
        import uuid
        from dutVulnScanner.core.schema import create_vulnerability_dict

        vulnerabilities = []

        if not output or not output.strip():
            return {"vulnerabilities": vulnerabilities, "metadata": {}}

        # Parse JSON lines
        subdomains = []
        for line in output.strip().split("\n"):
            try:
                data = json.loads(line)
                if "host" in data:
                    subdomains.append(data["host"])
            except json.JSONDecodeError:
                # Skip non-JSON lines
                continue

        # Create informational vulnerability for discovered subdomains
        if subdomains:
            vuln = create_vulnerability_dict(
                vuln_id=str(uuid.uuid4()),
                title="Subdomains Discovered",
                description=f"Found {len(subdomains)} subdomains",
                severity="info",
                host="",  # Will be filled by orchestrator
                port=None,
                service="subdomain-enumeration",
                detected_by="subfinder",
                evidence={"subdomains": subdomains, "count": len(subdomains)},
                remediation="Review exposed subdomains for sensitive information or services.",
            )
            vulnerabilities.append(vuln)

        return {
            "vulnerabilities": vulnerabilities,
            "metadata": {"subdomain_count": len(subdomains), "subdomains": subdomains},
        }
