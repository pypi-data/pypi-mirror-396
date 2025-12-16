"""Nmap adapter for network scanning."""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from datetime import datetime

from ..base import BaseAdapter
from dutVulnScanner.core.schema import create_vulnerability_dict


class NmapAdapter(BaseAdapter):
    """
    Adapter for Nmap network scanner.

    Executes nmap and parses XML output to extract:
    - Open ports
    - Service versions
    - OS detection
    - NSE script results (potential vulnerabilities)
    """

    name = "nmap"

    def run(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute nmap and return parsed results.

        Args:
            target: Target to scan
            options: Tool-specific options

        Returns:
            Scan results dictionary
        """
        import subprocess
        import tempfile
        import os

        # Create output file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        profile = options.get("profile", "scan")
        output_file = f"/tmp/nmap_{profile}_{timestamp}.xml"

        try:
            command = self.build_command(target, options, output_file)

            print(f"[DEBUG] Nmap command: {command}")
            print(f"[DEBUG] XML output file: {output_file}")

            # Get timeout: prioritize tool_config, then options, then default 600s
            timeout = self.tool_config.get("timeout", options.get("timeout", 600))

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0 and not self.allows_non_zero_exit():
                raise RuntimeError(f"{self._tool_name} failed with exit code {result.returncode}: {result.stderr}")

            # Parse output before deleting file
            parsed_result = self.parse_output(output_file)

            # Always keep XML file for debugging
            print(f"[DEBUG] Nmap XML saved at: {output_file}")

            return parsed_result

        except Exception as e:
            # Keep file on error for debugging
            if os.path.exists(output_file):
                print(f"[DEBUG] Error occurred. XML file kept at: {output_file}")
            raise

    @property
    def description(self) -> str:
        return "Network exploration and security auditing tool"

    def build_command(self, target: str, options: Dict[str, Any], output_file: str = None) -> str:
        """Build nmap command."""
        nmap_path = self.tool_config.get("path", "nmap")

        # Base arguments
        args = options.get("args", self.tool_config.get("default_args", ["-sV", "-sC"]))

        # Output format
        if output_file is None:
            output_file = options.get("output", "/tmp/nmap_output.xml")

        # Build command with proper quoting for shell safety
        cmd_parts = [nmap_path]

        # Quote arguments that contain special characters
        for arg in args:
            if "*" in arg or "?" in arg or " " in arg:
                cmd_parts.append(f"'{arg}'")
            else:
                cmd_parts.append(arg)

        cmd_parts.extend(["-oX", output_file])
        cmd_parts.append(target)

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse nmap XML output.

        Args:
            output: Path to XML output file from nmap

        Returns:
            Standardized results dictionary
        """
        vulnerabilities = []
        hosts = []
        all_ports = []
        all_services = []

        try:
            # Read XML from file
            tree = ET.parse(output)
            root = tree.getroot()

            # Parse each host
            for host in root.findall("host"):
                address_elem = host.find("address")
                if address_elem is None:
                    continue

                host_addr = address_elem.get("addr")

                # Get host status
                status = host.find("status")
                host_state = status.get("state") if status is not None else "unknown"

                # Collect host info
                host_info = {"address": host_addr, "state": host_state, "ports": []}

                # Parse ports
                for port in host.findall(".//port"):
                    port_id = port.get("portid")
                    protocol = port.get("protocol")

                    state = port.find("state")
                    port_state = state.get("state") if state is not None else "unknown"

                    service = port.find("service")
                    service_name = service.get("name") if service is not None else "unknown"
                    service_version = service.get("version", "") if service is not None else ""
                    service_product = service.get("product", "") if service is not None else ""

                    # Collect port info
                    port_info = {
                        "port": port_id,
                        "protocol": protocol,
                        "state": port_state,
                        "service": service_name,
                        "version": service_version,
                        "product": service_product,
                    }

                    host_info["ports"].append(port_info)
                    all_ports.append(port_info)

                    # Collect service info
                    if port_state == "open":
                        service_info = {
                            "host": host_addr,
                            "port": port_id,
                            "protocol": protocol,
                            "service": service_name,
                            "version": service_version,
                            "product": service_product,
                        }
                        all_services.append(service_info)

                    # Check for NSE scripts (vulnerabilities)
                    for script in port.findall("script"):
                        script_id = script.get("id")
                        script_output = script.get("output", "")

                        # Check if script indicates a vulnerability
                        if script_id and self._is_vulnerability_script(script_id):
                            vuln = create_vulnerability_dict(
                                title=f"Nmap: {script_id}",
                                description=script_output,
                                severity=self._get_script_severity(script_id),
                                host=host_addr or "unknown",
                                detected_by="nmap",
                                port=int(port_id) if port_id else 0,
                                protocol=protocol,
                                service=service_name,
                                evidence={
                                    "script_id": script_id,
                                    "service_version": service_version,
                                },
                            )
                            vulnerabilities.append(vuln)

                hosts.append(host_info)

                # Check OS detection for potential issues
                os_match = host.find(".//osmatch")
                if os_match is not None:
                    os_name = os_match.get("name", "")
                    host_info["os"] = os_name
                    if self._is_vulnerable_os(os_name):
                        vuln = create_vulnerability_dict(
                            title="Potentially outdated operating system",
                            description=f"Detected OS: {os_name}",
                            severity="info",
                            host=host_addr or "unknown",
                            detected_by="nmap",
                            evidence={"os": os_name},
                        )
                        vulnerabilities.append(vuln)

        except ET.ParseError as e:
            # If XML parsing fails, try to read from file
            pass

        return {
            "vulnerabilities": vulnerabilities,
            "hosts": hosts,
            "ports": all_ports,
            "services": all_services,
            "metadata": {
                "tool": "nmap",
                "scan_time": datetime.utcnow().isoformat(),
                "total_hosts": len(hosts),
                "total_open_ports": len(all_ports),
            },
        }

    def _is_vulnerability_script(self, script_id: str) -> bool:
        """Check if an NSE script indicates a vulnerability."""
        vuln_keywords = [
            "vuln",
            "exploit",
            "backdoor",
            "malware",
            "weak",
            "default",
            "anonymous",
            "vulnerability",
        ]
        return any(keyword in script_id.lower() for keyword in vuln_keywords)

    def _get_script_severity(self, script_id: str) -> str:
        """Determine severity based on script ID."""
        if "critical" in script_id.lower():
            return "critical"
        elif any(word in script_id.lower() for word in ["exploit", "backdoor", "malware"]):
            return "high"
        elif any(word in script_id.lower() for word in ["vuln", "weak"]):
            return "medium"
        else:
            return "low"

    def _is_vulnerable_os(self, os_name: str) -> bool:
        """Check if OS appears to be outdated or vulnerable."""
        vulnerable_keywords = [
            "Windows XP",
            "Windows 2003",
            "Windows 2000",
            "Linux 2.4",
            "Linux 2.6",
        ]
        return any(keyword in os_name for keyword in vulnerable_keywords)

    def get_docker_image(self) -> str:
        return "instrumentisto/nmap:latest"

    def allows_non_zero_exit(self) -> bool:
        """Nmap can exit with non-zero on certain conditions."""
        return True
