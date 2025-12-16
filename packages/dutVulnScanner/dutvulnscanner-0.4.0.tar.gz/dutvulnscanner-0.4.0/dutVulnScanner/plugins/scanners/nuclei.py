"""Nuclei adapter for vulnerability scanning."""
import json
from typing import Dict, Any
from datetime import datetime

from ..base import BaseAdapter
from dutVulnScanner.core.schema import create_vulnerability_dict


class NucleiAdapter(BaseAdapter):
    """
    Adapter for Nuclei vulnerability scanner.
    
    Nuclei uses templates to detect various vulnerabilities
    across web applications and infrastructure.
    """
    
    @property
    def description(self) -> str:
        return "Fast and customizable vulnerability scanner based on templates"
    
    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """Build nuclei command."""
        nuclei_path = self.tool_config.get("path", "nuclei")
        
        cmd_parts = [nuclei_path]
        
        # Target
        cmd_parts.extend(["-target", target])
        
        # Templates directory
        templates_dir = options.get("templates_dir") or self.tool_config.get("templates_dir")
        if templates_dir:
            cmd_parts.extend(["-t", templates_dir])
        
        # Severity filter
        severity = options.get("severity")
        if severity:
            cmd_parts.extend(["-severity", severity])
        
        # Output format (JSON)
        cmd_parts.extend(["-json"])
        
        # Additional options
        if options.get("silent", False):
            cmd_parts.append("-silent")
        
        if options.get("verbose", False):
            cmd_parts.append("-v")
        
        # Rate limiting
        rate_limit = options.get("rate_limit", 150)
        cmd_parts.extend(["-rate-limit", str(rate_limit)])
        
        # Timeout
        timeout = options.get("timeout", 5)
        cmd_parts.extend(["-timeout", str(timeout)])
        
        return " ".join(cmd_parts)
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse nuclei JSON output.
        
        Nuclei outputs one JSON object per line for each finding.
        
        Args:
            output: JSON Lines output from nuclei
            
        Returns:
            Standardized results dictionary
        """
        vulnerabilities = []
        
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            
            try:
                finding = json.loads(line)
                
                # Extract relevant information
                template_id = finding.get("template-id", "unknown")
                template_name = finding.get("info", {}).get("name", "Unknown")
                severity = finding.get("info", {}).get("severity", "info").lower()
                description = finding.get("info", {}).get("description", "")
                matched_at = finding.get("matched-at", "")
                host = finding.get("host", "")
                
                # Extract CVE/CWE IDs
                cve_ids = finding.get("info", {}).get("classification", {}).get("cve-id", [])
                cwe_ids = finding.get("info", {}).get("classification", {}).get("cwe-id", [])
                
                if not isinstance(cve_ids, list):
                    cve_ids = [cve_ids] if cve_ids else []
                if not isinstance(cwe_ids, list):
                    cwe_ids = [cwe_ids] if cwe_ids else []
                
                # Extract references
                references = finding.get("info", {}).get("reference", [])
                if isinstance(references, str):
                    references = [references]
                
                # Create vulnerability entry
                vuln = create_vulnerability_dict(
                    title=template_name,
                    description=description or f"Nuclei template: {template_id}",
                    severity=severity,
                    host=host,
                    detected_by="nuclei",
                    id=f"nuclei-{template_id}",
                    cve_ids=cve_ids,
                    cwe_ids=cwe_ids,
                    references=references,
                    evidence={
                        "template_id": template_id,
                        "matched_at": matched_at,
                        "matcher_name": finding.get("matcher-name", ""),
                        "type": finding.get("type", ""),
                    },
                )
                
                vulnerabilities.append(vuln)
                
            except json.JSONDecodeError:
                continue
        
        return {
            "vulnerabilities": vulnerabilities,
            "metadata": {
                "tool": "nuclei",
                "scan_time": datetime.utcnow().isoformat(),
            },
        }
    
    def get_docker_image(self) -> str:
        return "projectdiscovery/nuclei:latest"
    
    def allows_non_zero_exit(self) -> bool:
        """Nuclei exits with non-zero when vulnerabilities are found."""
        return True
    
    def get_default_options(self) -> Dict[str, Any]:
        return {
            "silent": True,
            "rate_limit": 150,
            "timeout": 5,
        }
