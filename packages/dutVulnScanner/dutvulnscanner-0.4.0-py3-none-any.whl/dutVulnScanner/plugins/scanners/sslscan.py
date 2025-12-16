"""SSLScan adapter for SSL/TLS security testing."""

import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import Vulnerability, SeverityLevel


class SslscanAdapter(BaseAdapter):
    """Adapter for SSLScan SSL/TLS scanner."""

    name = "sslscan"

    @property
    def description(self) -> str:
        return "SSL/TLS configuration and vulnerability scanner"

    @property
    def category(self) -> str:
        return "vulnerability_exploitation"

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build sslscan command.

        Args:
            target: Target host:port
            options: SSLScan options

        Returns:
            Command string
        """
        cmd_parts = ["sslscan"]

        # XML output
        cmd_parts.append("--xml=-")

        # Show certificate info
        if options.get("show_certificate", True):
            cmd_parts.append("--show-certificate")

        # Check for vulnerabilities
        if options.get("check_vulnerabilities", True):
            cmd_parts.append("--show-ciphers")

        # Target
        cmd_parts.append(target)

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse sslscan XML output.

        Args:
            output: Raw sslscan XML output

        Returns:
            Parsed vulnerabilities and SSL/TLS info
        """
        vulnerabilities = []
        ssl_info = {"protocols": [], "ciphers": [], "certificate": {}, "vulnerabilities_found": []}

        try:
            root = ET.fromstring(output)

            # Parse protocols
            for protocol in root.findall(".//protocol"):
                proto_info = {
                    "type": protocol.get("type"),
                    "version": protocol.get("version"),
                    "enabled": protocol.get("enabled") == "1",
                }
                ssl_info["protocols"].append(proto_info)

                # Check for outdated protocols
                if proto_info["enabled"] and proto_info["version"] in ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]:
                    vuln = Vulnerability(
                        id=str(uuid.uuid4()),
                        title=f"Insecure SSL/TLS Protocol: {proto_info['version']}",
                        description=f"The server supports outdated and insecure protocol {proto_info['version']}",
                        severity=SeverityLevel.HIGH if "SSL" in proto_info["version"] else SeverityLevel.MEDIUM,
                        cvss_score=7.5 if "SSL" in proto_info["version"] else 5.3,
                        host="",
                        port=None,
                        protocol="ssl/tls",
                        service="https",
                        detected_by=self.name,
                        detection_time=datetime.utcnow().isoformat(),
                        evidence={"protocol": proto_info},
                        remediation=f"Disable {proto_info['version']} and use TLS 1.2 or higher",
                        references=["https://www.rfc-editor.org/rfc/rfc7568"],
                    )
                    vulnerabilities.append(vuln.dict())
                    ssl_info["vulnerabilities_found"].append(f"Weak protocol: {proto_info['version']}")

            # Parse ciphers
            for cipher in root.findall(".//cipher"):
                cipher_info = {
                    "name": cipher.get("cipher"),
                    "strength": cipher.get("strength"),
                    "status": cipher.get("status"),
                }
                ssl_info["ciphers"].append(cipher_info)

                # Check for weak ciphers (null-safe name check)
                name = cipher_info.get("name") or ""
                if cipher_info.get("status") == "accepted" and any(
                    token in name for token in ("NULL", "EXPORT", "DES")
                ):
                    vuln = Vulnerability(
                        id=str(uuid.uuid4()),
                        title=f"Weak Cipher Suite: {cipher_info['name']}",
                        description=f"The server accepts weak cipher suite: {cipher_info['name']}",
                        severity=SeverityLevel.HIGH,
                        cvss_score=7.5,
                        host="",
                        port=None,
                        protocol="ssl/tls",
                        service="https",
                        detected_by=self.name,
                        detection_time=datetime.utcnow().isoformat(),
                        evidence={"cipher": cipher_info},
                        remediation="Disable weak cipher suites and use only strong modern ciphers",
                        references=["https://www.rfc-editor.org/rfc/rfc7525"],
                    )
                    vulnerabilities.append(vuln.dict())
                    ssl_info["vulnerabilities_found"].append(f"Weak cipher: {cipher_info['name']}")

            # Parse certificate
            cert = root.find(".//certificate")
            if cert is not None:
                ssl_info["certificate"] = {
                    "subject": cert.findtext("subject", ""),
                    "issuer": cert.findtext("issuer", ""),
                    "not_before": cert.findtext("not-valid-before", ""),
                    "not_after": cert.findtext("not-valid-after", ""),
                    "signature_algorithm": cert.findtext("signature-algorithm", ""),
                }

        except ET.ParseError as e:
            # If XML parsing fails, try text parsing
            lines = output.strip().split("\n")
            for line in lines:
                if "SSLv2" in line or "SSLv3" in line:
                    ssl_info["vulnerabilities_found"].append(f"Detected in output: {line.strip()}")

        return {
            "ssl_info": ssl_info,
            "vulnerabilities": vulnerabilities,
            "metadata": {
                "tool": self.name,
                "category": self.category,
            },
        }

    def get_docker_image(self) -> str:
        """Get Docker image name."""
        return "mozilla/sslscan"
