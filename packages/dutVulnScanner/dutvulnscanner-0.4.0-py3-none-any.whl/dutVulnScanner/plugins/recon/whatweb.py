"""WhatWeb adapter for web technology detection."""

import json
from typing import Dict, Any, List
from datetime import datetime

from ..base import BaseAdapter
from dutVulnScanner.core.schema import create_vulnerability_dict


class WhatWebAdapter(BaseAdapter):
    """
    Adapter for WhatWeb web technology identifier.

    WhatWeb identifies technologies, CMS, frameworks, and versions
    used by websites. Can detect outdated or vulnerable components.
    """

    name = "whatweb"

    @property
    def description(self) -> str:
        return "Web technology and version detection tool"

    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """Build whatweb command."""
        whatweb_path = self.tool_config.get("path", "whatweb")

        cmd_parts = [whatweb_path]

        # Target
        cmd_parts.append(target)

        # Aggression level (1-4)
        aggression = options.get("aggression", 1)
        cmd_parts.extend(["-a", str(aggression)])

        # Output format (JSON)
        cmd_parts.extend(["--log-json=-"])

        # User agent
        user_agent = options.get("user_agent")
        if user_agent:
            cmd_parts.extend(["--user-agent", user_agent])

        # Follow redirects
        if options.get("follow_redirect", True):
            cmd_parts.append("--follow-redirect=always")

        # Rate limiting (wait between requests in seconds)
        wait_time = options.get("wait", 1)
        cmd_parts.extend(["--max-threads", "1"])
        cmd_parts.extend(["--wait", str(wait_time)])

        # Connection timeout per request
        conn_timeout = options.get("conn_timeout", 30)
        cmd_parts.extend(["--open-timeout", str(conn_timeout)])

        cmd = " ".join(cmd_parts)
        print(f"[DEBUG] WhatWeb command: {cmd}")

        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse whatweb JSON output.

        Args:
            output: JSON output from whatweb

        Returns:
            Standardized results dictionary
        """

        # Save raw output to file for debugging
        import tempfile
        import os

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        debug_file = f"/tmp/whatweb_debug_{timestamp}.json"
        try:
            with open(debug_file, "w") as f:
                f.write(output)
            print(f"[DEBUG] WhatWeb full output saved to: {debug_file}")
        except Exception as e:
            print(f"[DEBUG] Could not save debug file: {e}")

        vulnerabilities = []
        technologies = []

        try:
            # WhatWeb outputs mixed format: JSON + plain text inside array
            # Need to extract only the JSON objects
            lines = output.strip().split("\n")

            json_objects = []
            for line in lines:
                line = line.strip()
                # Skip empty lines, array brackets, and plain text summaries
                if not line or line == "[" or line == "]":
                    continue
                # Try to parse as JSON object
                if line.startswith("{"):
                    # Remove trailing comma if exists
                    line = line.rstrip(",")
                    try:
                        obj = json.loads(line)
                        json_objects.append(obj)
                    except json.JSONDecodeError:
                        # Skip non-JSON lines
                        continue

            print(f"[DEBUG] Parsed {len(json_objects)} JSON objects from output")

            for data in json_objects:
                target = data.get("target", "")
                plugins = data.get("plugins", {})

                # Track detected technologies
                for plugin_name, plugin_data in plugins.items():
                    if not isinstance(plugin_data, dict):
                        continue

                    version = plugin_data.get("version", [""])[0] if "version" in plugin_data else None

                    tech = {
                        "name": plugin_name,
                        "version": version,
                    }
                    technologies.append(tech)

                    print(f"[DEBUG] Detected technology: {plugin_name} v{version}")

                    # Check for known vulnerable versions
                    if version and self._is_vulnerable_version(plugin_name, version):
                        print(f"[DEBUG] *** VULNERABLE: {plugin_name} v{version} ***")
                        vuln = create_vulnerability_dict(
                            title=f"Outdated {plugin_name} version detected",
                            description=f"{plugin_name} version {version} may contain known vulnerabilities",
                            severity=self._get_tech_severity(plugin_name),
                            host=target,
                            detected_by="whatweb",
                            evidence={
                                "technology": plugin_name,
                                "version": version,
                                "details": plugin_data,
                            },
                            remediation=f"Update {plugin_name} to the latest version",
                        )
                        vulnerabilities.append(vuln)

                    # Check for security headers
                    if plugin_name in ["HTTPServer", "X-Powered-By"]:
                        string_data = plugin_data.get("string", [""])
                        if string_data and any(s in str(string_data).lower() for s in string_data):
                            vuln = create_vulnerability_dict(
                                title="Server information disclosure",
                                description=f"Server banner reveals: {string_data}",
                                severity="low",
                                host=target,
                                detected_by="whatweb",
                                evidence={
                                    "header": plugin_name,
                                    "value": string_data,
                                },
                                remediation="Remove or obfuscate server version information",
                            )
                            vulnerabilities.append(vuln)

        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON decode error: {e}")
            print(f"[DEBUG] Failed to parse output")
        except Exception as e:
            print(f"[DEBUG] Unexpected error in parse_output: {type(e).__name__}: {e}")

        print(f"[DEBUG] Total technologies detected: {len(technologies)}")
        print(f"[DEBUG] Total vulnerabilities found: {len(vulnerabilities)}")

        return {
            "vulnerabilities": vulnerabilities,
            "metadata": {
                "tool": "whatweb",
                "scan_time": datetime.utcnow().isoformat(),
                "technologies": technologies,
            },
        }

    def _is_vulnerable_version(self, tech: str, version: str) -> bool:
        """
        Check if a technology version is known to be vulnerable.

        This is a simple check. In production, this should query
        a vulnerability database.
        """
        # Simple heuristic: very old versions (case-insensitive)
        vulnerable_patterns = {
            "wordpress": ["3.", "4.0", "4.1", "4.2", "4.3", "4.4", "4.5"],
            "jquery": ["1.", "2."],
            "bootstrap": ["2.", "3.0", "3.1", "3.2", "3.3"],
            "apache": ["2.2", "2.0"],
            "nginx": [
                "1.0",
                "1.1",
                "1.2",
                "1.3",
                "1.4",
                "1.5",
                "1.6",
                "1.7",
                "1.8",
                "1.9",
                "1.10",
                "1.11",
                "1.12",
                "1.13",
                "1.14",
                "1.15",
                "1.16",
                "1.17",
                "1.18",
            ],
            "php": ["5.", "7.0", "7.1"],
            "mysql": ["5.0", "5.1", "5.5"],
        }

        tech_lower = tech.lower()
        if tech_lower in vulnerable_patterns:
            return any(version.startswith(pattern) for pattern in vulnerable_patterns[tech_lower])

        return False

    def _get_tech_severity(self, tech: str) -> str:
        """Determine severity based on technology type."""
        critical_tech = ["WordPress", "Joomla", "Drupal", "PHP", "Apache"]

        if tech in critical_tech:
            return "high"
        else:
            return "medium"

    def get_docker_image(self) -> str:
        return "urbanadventurer/whatweb:latest"

    def get_default_options(self) -> Dict[str, Any]:
        return {
            "aggression": 1,
            "follow_redirect": True,
            "timeout": 30,
        }
