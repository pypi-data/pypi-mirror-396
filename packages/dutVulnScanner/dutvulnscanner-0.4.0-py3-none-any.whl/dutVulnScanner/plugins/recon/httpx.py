"""HTTPX adapter for HTTP probing and fingerprinting."""

import subprocess
import json
from typing import Dict, Any, List
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.schema import Vulnerability


class HttpxAdapter(BaseAdapter):
    """
    HTTPX adapter for HTTP probing.

    HTTPX is a fast and multi-purpose HTTP toolkit that allows running multiple
    probers using retryable http library. It probes for HTTP/HTTPS and collects
    information like status codes, titles, tech stack, etc.
    """

    @property
    def name(self) -> str:
        return "httpx"

    @property
    def description(self) -> str:
        return "HTTP probing and fingerprinting tool"

    @property
    def required_tools(self) -> List[str]:
        return ["httpx"]

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build httpx command.

        Args:
            target: URL or host to probe
            options: Configuration dictionary with options:
                - ports: Ports to probe (e.g., "80,443,8080")
                - threads: Number of threads (default: 50)
                - timeout: Timeout in seconds (default: 10)
                - follow_redirects: Follow redirects (default: true)
                - tech_detect: Detect technologies (default: true)
                - status_code: Show status codes
                - title: Extract page titles
                - web_server: Extract web server info

        Returns:
            Command string for subprocess
        """
        cmd_parts = ["httpx", "-u", target, "-json"]

        # Port configuration
        ports = options.get("ports")
        if ports:
            cmd_parts.extend(["-ports", ports])

        # Threading
        threads = options.get("threads", 50)
        cmd_parts.extend(["-threads", str(threads)])

        # Timeout
        timeout = options.get("timeout", 10)
        cmd_parts.extend(["-timeout", str(timeout)])

        # Follow redirects
        if options.get("follow_redirects", True):
            cmd_parts.append("-follow-redirects")

        # Technology detection
        if options.get("tech_detect", True):
            cmd_parts.append("-tech-detect")

        # Status code
        if options.get("status_code", True):
            cmd_parts.append("-status-code")

        # Title extraction
        if options.get("title", True):
            cmd_parts.append("-title")

        # Web server
        if options.get("web_server", True):
            cmd_parts.append("-web-server")

        # Extract various information
        cmd_parts.extend(["-content-length", "-method", "-ip", "-cname"])

        # Silent mode
        cmd_parts.append("-silent")

        return " ".join(cmd_parts)

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse httpx JSON output.

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
        http_services = []
        for line in output.strip().split("\n"):
            try:
                data = json.loads(line)

                url = data.get("url", "")
                status_code = data.get("status_code", 0)
                title = data.get("title", "")
                web_server = data.get("webserver", "")
                tech = data.get("tech", [])
                content_length = data.get("content_length", 0)

                # Determine severity based on findings
                severity = "info"
                issues = []

                # Check for security headers
                if "header" in data:
                    headers = data["header"]
                    if "X-Frame-Options" not in headers:
                        issues.append("Missing X-Frame-Options header")
                        severity = "low"
                    if "X-Content-Type-Options" not in headers:
                        issues.append("Missing X-Content-Type-Options header")
                    if "Strict-Transport-Security" not in headers and url.startswith("https"):
                        issues.append("Missing HSTS header")
                        severity = "low"

                # Check status codes
                if status_code >= 500:
                    issues.append(f"Server error: {status_code}")
                    severity = "medium"
                elif status_code == 403:
                    issues.append("Access forbidden - potential misconfiguration")

                title_text = "HTTP Service Discovered" if not issues else "HTTP Security Issues Detected"
                description = f"Found HTTP service at {url}"
                if issues:
                    description += f" with issues: {', '.join(issues)}"

                vuln = create_vulnerability_dict(
                    vuln_id=str(uuid.uuid4()),
                    title=title_text,
                    description=description,
                    severity=severity,
                    host=data.get("host", ""),
                    port=data.get("port", 80 if url.startswith("http:") else 443),
                    service="web",
                    detected_by="httpx",
                    evidence={
                        "url": url,
                        "status_code": status_code,
                        "title": title,
                        "web_server": web_server,
                        "technologies": tech,
                        "content_length": content_length,
                        "issues": issues,
                    },
                    remediation="Review HTTP headers and implement security best practices. Add missing security headers.",
                )
                vulnerabilities.append(vuln)
                http_services.append(data)

            except json.JSONDecodeError:
                continue

        return {
            "vulnerabilities": vulnerabilities,
            "metadata": {"http_service_count": len(http_services), "urls": [s.get("url") for s in http_services]},
        }
