"""Naabu adapter for fast port scanning."""

import subprocess
import json
from typing import Dict, Any, List
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import Vulnerability


class NaabuAdapter(BaseAdapter):
    """
    Naabu adapter for fast port scanning.

    Naabu is a port scanning tool written in Go that allows you to enumerate
    valid ports for hosts in a fast and reliable manner. It's faster than nmap
    for initial port discovery.
    """

    @property
    def name(self) -> str:
        return "naabu"

    @property
    def description(self) -> str:
        return "Fast port scanner for discovering open ports"

    @property
    def required_tools(self) -> List[str]:
        return ["naabu"]

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build naabu command.

        Args:
            target: Host or IP to scan
            options: Configuration dictionary with options:
                - ports: Port range (e.g., "1-65535", "top-1000")
                - rate: Packets per second (default: 1000)
                - timeout: Timeout in milliseconds (default: 1000)
                - retries: Number of retries (default: 3)
                - scan_all_ips: Scan all IPs associated with DNS records
                - exclude_cdn: Skip CDN/WAF IPs

        Returns:
            Command string for subprocess
        """
        cmd_parts = ["naabu", "-host", target, "-json"]

        # Port configuration
        ports = options.get("ports", "top-1000")
        if ports == "top-1000":
            cmd_parts.extend(["-top-ports", "1000"])
        elif ports == "full":
            cmd_parts.extend(["-p", "-"])  # All ports
        else:
            cmd_parts.extend(["-p", ports])

        # Rate limiting
        rate = options.get("rate", 1000)
        cmd_parts.extend(["-rate", str(rate)])

        # Timeout
        timeout = options.get("timeout", 1000)
        cmd_parts.extend(["-timeout", str(timeout)])

        # Retries
        retries = options.get("retries", 3)
        cmd_parts.extend(["-retries", str(retries)])

        # Scan all IPs
        if options.get("scan_all_ips", False):
            cmd_parts.append("-scan-all-ips")

        # Exclude CDN
        if options.get("exclude_cdn", True):
            cmd_parts.append("-exclude-cdn")

        # Silent mode
        cmd_parts.append("-silent")

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse naabu JSON output.

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
        open_ports = []
        for line in output.strip().split("\n"):
            try:
                data = json.loads(line)
                if "port" in data:
                    port_info = {"port": data["port"], "host": data.get("host", ""), "ip": data.get("ip", "")}
                    open_ports.append(port_info)
            except json.JSONDecodeError:
                continue

        # Create vulnerability for each open port
        for port_data in open_ports:
            vuln = create_vulnerability_dict(
                vuln_id=str(uuid.uuid4()),
                title=f"Open Port Detected: {port_data['port']}",
                description=f"Port {port_data['port']} is open",
                severity="info",
                host=port_data["host"],
                port=port_data["port"],
                service="unknown",
                detected_by="naabu",
                evidence={"port": port_data["port"], "ip": port_data["ip"]},
                remediation="Verify if this port should be exposed. Run service detection with nmap.",
            )
            vulnerabilities.append(vuln)

        return {
            "vulnerabilities": vulnerabilities,
            "metadata": {"open_port_count": len(open_ports), "ports": [p["port"] for p in open_ports]},
        }
