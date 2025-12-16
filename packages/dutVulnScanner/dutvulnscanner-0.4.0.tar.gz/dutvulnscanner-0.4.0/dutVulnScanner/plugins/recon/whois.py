"""WHOIS adapter for domain reconnaissance."""

import subprocess
import json
from typing import Dict, Any, List
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import Vulnerability


class WhoisAdapter(BaseAdapter):
    """Adapter for WHOIS domain information gathering."""

    name = "whois"
    category = "reconnaissance"

    @property
    def description(self) -> str:
        return "Domain registration and ownership information"

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build WHOIS command.

        Args:
            target: Domain name to lookup
            options: Additional options

        Returns:
            Command string
        """
        cmd_parts = ["whois", target]
        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse WHOIS output.

        Args:
            output: Raw WHOIS output

        Returns:
            Parsed results with domain information
        """
        vulnerabilities = []
        domain_info = {}

        lines = output.strip().split("\n")

        for line in lines:
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                domain_info[key] = value

        # Check for expired or soon-to-expire domains
        if "expiry_date" in domain_info or "registry_expiry_date" in domain_info:
            expiry = domain_info.get("expiry_date") or domain_info.get("registry_expiry_date")
            # Could add logic to check if expiring soon

        return {
            "domain_info": domain_info,
            "vulnerabilities": vulnerabilities,
            "metadata": {
                "tool": self.name,
                "category": self.category,
            },
        }

    def get_docker_image(self) -> str:
        """Get Docker image name."""
        return "alpine:latest"  # whois is available in alpine
