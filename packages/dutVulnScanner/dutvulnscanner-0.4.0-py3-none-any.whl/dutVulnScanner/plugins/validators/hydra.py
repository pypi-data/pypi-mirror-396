"""Hydra adapter for password brute-forcing."""

import uuid
from datetime import datetime
from typing import Dict, Any
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import Vulnerability, SeverityLevel


class HydraAdapter(BaseAdapter):
    """Adapter for THC-Hydra password cracker."""

    name = "hydra"

    @property
    def description(self) -> str:
        return "Network authentication brute-force tool"

    @property
    def category(self) -> str:
        return "vulnerability_exploitation"

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build Hydra command.

        Args:
            target: Target host
            options: Hydra options

        Returns:
            Command string
        """
        cmd_parts = ["hydra"]

        # Username
        username = options.get("username", "admin")
        if username:
            cmd_parts.extend(["-l", username])

        # Password list
        password_list = options.get("password_list", "/usr/share/wordlists/rockyou.txt")
        cmd_parts.extend(["-P", password_list])

        # Threads
        threads = options.get("threads", 4)
        cmd_parts.extend(["-t", str(threads)])

        # Service
        service = options.get("service", "ssh")

        # Verbosity
        cmd_parts.append("-V")

        # Output format
        cmd_parts.extend(["-o", "/tmp/hydra_output.txt"])

        # Target and service
        cmd_parts.extend([target, service])

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse Hydra output.

        Args:
            output: Raw Hydra output

        Returns:
            Parsed vulnerabilities and cracked credentials
        """
        vulnerabilities = []
        findings = {"cracked_credentials": [], "service": None, "attempts": 0}

        lines = output.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Detect successful login
            if (
                "[" in line
                and "]" in line
                and "host:" in line.lower()
                and ("login:" in line.lower() or "password:" in line.lower())
            ):
                # Parse: [22][ssh] host: 192.168.1.1   login: admin   password: password123
                parts = line.split()
                host = ""
                login = ""
                password = ""
                service = ""

                for i, part in enumerate(parts):
                    if part.lower() == "host:":
                        host = parts[i + 1] if i + 1 < len(parts) else ""
                    elif part.lower() == "login:":
                        login = parts[i + 1] if i + 1 < len(parts) else ""
                    elif part.lower() == "password:":
                        password = parts[i + 1] if i + 1 < len(parts) else ""
                    elif "][" in part:
                        service = part.split("][")[1].replace("]", "")

                if login and password:
                    findings["cracked_credentials"].append(
                        {"host": host, "service": service, "login": login, "password": password}
                    )
                    findings["service"] = service

                    vuln = Vulnerability(
                        id=str(uuid.uuid4()),
                        title=f"Weak Authentication: {service.upper()}",
                        description=f"Successfully brute-forced {service} credentials. Login: {login}, Password: {password}",
                        severity=SeverityLevel.CRITICAL,
                        cvss_score=9.8,
                        host=host,
                        port=None,
                        protocol="tcp",
                        service=service,
                        detected_by=self.name,
                        detection_time=datetime.utcnow().isoformat(),
                        evidence={"username": login, "password": password, "method": "brute_force"},
                        remediation="Change to a strong password, implement account lockout, use multi-factor authentication",
                        references=["https://owasp.org/www-project-top-ten/"],
                    )
                    vulnerabilities.append(vuln.dict())

            # Count attempts
            if "attempt" in line.lower() or "trying" in line.lower():
                findings["attempts"] += 1

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
        return "vanhauser/hydra"
