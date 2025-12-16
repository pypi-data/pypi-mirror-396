"""Nikto adapter for web server vulnerability scanning."""

import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import create_vulnerability_dict


class NiktoAdapter(BaseAdapter):
    """
    Nikto adapter for web server scanning.

    Nikto is a web server scanner which performs comprehensive tests against
    web servers for multiple items, including over 6700 potentially dangerous
    files/programs, checks for outdated versions, and version specific problems.
    """

    @property
    def name(self) -> str:
        return "nikto"

    @property
    def description(self) -> str:
        return "Web server vulnerability scanner for misconfigurations and outdated software"

    @property
    def required_tools(self) -> List[str]:
        return ["nikto"]

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build nikto command.

        Args:
            target: URL or host to scan
            options: Configuration dictionary with options:
                - port: Port to scan (default: 80)
                - ssl: Use SSL (default: auto-detect)
                - tuning: Tuning options (e.g., "x" for reverse proxy)
                - timeout: Timeout in seconds (default: 10)
                - evasion: IDS evasion technique

        Returns:
            Command string for subprocess
        """
        cmd_parts = ["nikto"]

        # Target host
        cmd_parts.extend(["-h", target])

        # Port
        port = options.get("port", 80)
        cmd_parts.extend(["-p", str(port)])

        # SSL
        if options.get("ssl") or port == 443:
            cmd_parts.append("-ssl")

        # Tuning options
        tuning = options.get("tuning")
        if tuning:
            cmd_parts.extend(["-Tuning", tuning])

        # Timeout
        timeout = options.get("timeout", 10)
        cmd_parts.extend(["-timeout", str(timeout)])

        # Evasion
        evasion = options.get("evasion")
        if evasion:
            cmd_parts.extend(["-evasion", evasion])

        # Output format - XML for parsing
        cmd_parts.extend(["-Format", "xml"])
        cmd_parts.extend(["-output", "-"])

        # No interactive prompts
        cmd_parts.append("-ask no")

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse nikto XML output.

        Args:
            output: Raw command output (XML)

        Returns:
            Dictionary with vulnerabilities and metadata
        """
        from datetime import datetime
        import uuid

        vulnerabilities = []

        if not output or not output.strip():
            return {"vulnerabilities": vulnerabilities, "metadata": {}}

        try:
            # Parse XML
            root = ET.fromstring(output)

            # Extract scan items
            for item in root.findall(".//item"):
                osvdb_id = item.get("osvdbid", "")
                method = item.get("method", "GET")

                description_elem = item.find("description")
                uri_elem = item.find("uri")
                namelink_elem = item.find("namelink")

                description = description_elem.text if description_elem is not None else "Web server issue detected"
                uri = uri_elem.text if uri_elem is not None else ""
                namelink = namelink_elem.text if namelink_elem is not None else ""

                # Determine severity based on description keywords
                severity = "info"
                desc_lower = description.lower()

                if any(word in desc_lower for word in ["critical", "exploit", "backdoor", "shell"]):
                    severity = "critical"
                elif any(word in desc_lower for word in ["vulnerable", "security", "injection"]):
                    severity = "high"
                elif any(word in desc_lower for word in ["outdated", "misconfiguration", "weak"]):
                    severity = "medium"
                elif any(word in desc_lower for word in ["disclosure", "enumeration"]):
                    severity = "low"

                vuln = create_vulnerability_dict(
                    vuln_id=str(uuid.uuid4()),
                    title=namelink if namelink else "Web Server Issue",
                    description=description,
                    severity=severity,
                    host="",  # Will be filled by orchestrator
                    port=None,
                    service="web",
                    detected_by="nikto",
                    evidence={"uri": uri, "method": method, "osvdb_id": osvdb_id},
                    remediation="Review the finding and apply appropriate patches or configuration changes.",
                )
                vulnerabilities.append(vuln)

        except ET.ParseError as e:
            # If XML parsing fails, return empty results
            pass

        return {"vulnerabilities": vulnerabilities, "metadata": {"nikto_findings_count": len(vulnerabilities)}}
