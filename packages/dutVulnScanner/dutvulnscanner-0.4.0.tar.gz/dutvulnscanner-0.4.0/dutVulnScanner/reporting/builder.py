"""Report builder for multiple output formats."""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class ReportBuilder:
    """
    Builds reports in various formats from scan results.
    
    Supported formats:
    - JSON: Machine-readable format
    - HTML: Human-readable web report
    - PDF: Printable document
    - SARIF: Static Analysis Results Interchange Format
    """
    
    def __init__(self):
        """Initialize report builder."""
        self.results = None
        self.template_dir = Path(__file__).parent / "templates"
    
    def load_results(self, results_file: Path):
        """
        Load scan results from file.
        
        Args:
            results_file: Path to JSON results file
        """
        with open(results_file, "r") as f:
            self.results = json.load(f)
    
    def generate(
        self,
        output_file: Path,
        format: str = "html",
        template: str = "default",
    ):
        """
        Generate a report in the specified format.
        
        Args:
            output_file: Output file path
            format: Output format (html, pdf, json, sarif)
            template: Template name to use
        """
        if self.results is None:
            raise ValueError("No results loaded. Call load_results() first.")
        
        format = format.lower()
        
        if format == "json":
            self._generate_json(output_file)
        elif format == "html":
            self._generate_html(output_file, template)
        elif format == "pdf":
            self._generate_pdf(output_file, template)
        elif format == "sarif":
            self._generate_sarif(output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_json(self, output_file: Path):
        """Generate JSON report."""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
    
    def _generate_html(self, output_file: Path, template: str):
        """Generate HTML report."""
        template_file = self.template_dir / f"{template}.html"
        
        if not template_file.exists():
            template_file = self.template_dir / "default.html"
        
        # Read template
        with open(template_file, "r", encoding="utf-8") as f:
            template_content = f.read()
        
        # Prepare data
        html = self._render_html_template(template_content)
        
        # Write output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
    
    def _render_html_template(self, template: str) -> str:
        """Render HTML template with results data."""
        # Simple template rendering
        # In production, use a proper template engine like Jinja2
        
        # Summary statistics
        stats = self.results.get("statistics", {})
        vulns = self.results.get("vulnerabilities", [])
        
        # Build severity breakdown HTML
        severity_html = ""
        for severity, count in stats.get("by_severity", {}).items():
            color = self._get_severity_color(severity)
            severity_html += f"""
            <div class="severity-item">
                <span class="severity-badge {severity}" style="background-color: {color}">
                    {severity.upper()}: {count}
                </span>
            </div>
            """
        
        # Build vulnerabilities table HTML
        vulns_html = ""
        for vuln in vulns:
            severity = vuln.get("severity", "info")
            color = self._get_severity_color(severity)
            
            vulns_html += f"""
            <tr>
                <td><span class="severity-badge {severity}" style="background-color: {color}">{severity.upper()}</span></td>
                <td><strong>{vuln.get('title', 'N/A')}</strong></td>
                <td>{vuln.get('host', 'N/A')}</td>
                <td>{vuln.get('port', '-')}</td>
                <td>{vuln.get('detected_by', 'N/A')}</td>
            </tr>
            <tr class="vuln-details">
                <td colspan="5">
                    <p>{vuln.get('description', 'No description')}</p>
                    {self._render_cve_ids(vuln.get('cve_ids', []))}
                    {self._render_remediation(vuln.get('remediation'))}
                </td>
            </tr>
            """
        
        # Replace placeholders
        html = template.replace("{{SCAN_ID}}", self.results.get("scan_id", "N/A"))
        html = html.replace("{{TARGET}}", self.results.get("target", "N/A"))
        html = html.replace("{{PROFILE}}", self.results.get("profile", "N/A"))
        html = html.replace("{{START_TIME}}", self.results.get("start_time", "N/A"))
        html = html.replace("{{DURATION}}", f"{self.results.get('duration', 0):.2f}s")
        html = html.replace("{{TOTAL_VULNS}}", str(stats.get("total", 0)))
        html = html.replace("{{SEVERITY_BREAKDOWN}}", severity_html)
        html = html.replace("{{VULNERABILITIES_TABLE}}", vulns_html)
        html = html.replace("{{TOOLS_USED}}", ", ".join(self.results.get("tools_used", [])))
        
        return html
    
    def _generate_pdf(self, output_file: Path, template: str):
        """Generate PDF report."""
        # First generate HTML
        html_file = output_file.with_suffix(".html")
        self._generate_html(html_file, template)
        
        # Convert HTML to PDF using a library like weasyprint or pdfkit
        # For now, just note that PDF generation requires additional dependencies
        try:
            from weasyprint import HTML
            HTML(str(html_file)).write_pdf(str(output_file))
        except ImportError:
            raise ImportError(
                "PDF generation requires weasyprint. "
                "Install it with: pip install weasyprint"
            )
    
    def _generate_sarif(self, output_file: Path):
        """Generate SARIF (Static Analysis Results Interchange Format) report."""
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "DUTVulnScanner",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/DinhManhAVG/DUTVulnScanner",
                        }
                    },
                    "results": self._convert_to_sarif_results(),
                }
            ],
        }
        
        with open(output_file, "w") as f:
            json.dump(sarif, f, indent=2)
    
    def _convert_to_sarif_results(self) -> List[Dict[str, Any]]:
        """Convert vulnerabilities to SARIF results format."""
        sarif_results = []
        
        for vuln in self.results.get("vulnerabilities", []):
            result = {
                "ruleId": vuln.get("id", "unknown"),
                "level": self._severity_to_sarif_level(vuln.get("severity", "info")),
                "message": {
                    "text": vuln.get("description", "")
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "address": {
                                "fullyQualifiedName": vuln.get("host", ""),
                            }
                        }
                    }
                ],
                "properties": {
                    "detected_by": vuln.get("detected_by", ""),
                    "port": vuln.get("port"),
                    "service": vuln.get("service"),
                    "cve_ids": vuln.get("cve_ids", []),
                    "cwe_ids": vuln.get("cwe_ids", []),
                },
            }
            sarif_results.append(result)
        
        return sarif_results
    
    def _severity_to_sarif_level(self, severity: str) -> str:
        """Convert severity to SARIF level."""
        mapping = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note",
        }
        return mapping.get(severity.lower(), "note")
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level."""
        colors = {
            "critical": "#d32f2f",
            "high": "#f57c00",
            "medium": "#fbc02d",
            "low": "#0288d1",
            "info": "#5e35b1",
        }
        return colors.get(severity.lower(), "#666")
    
    def _render_cve_ids(self, cve_ids: List[str]) -> str:
        """Render CVE IDs as HTML."""
        if not cve_ids:
            return ""
        
        links = []
        for cve_id in cve_ids:
            url = f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}"
            links.append(f'<a href="{url}" target="_blank">{cve_id}</a>')
        
        return f"<p><strong>CVE IDs:</strong> {', '.join(links)}</p>"
    
    def _render_remediation(self, remediation: str) -> str:
        """Render remediation advice as HTML."""
        if not remediation:
            return ""
        
        return f'<p><strong>Remediation:</strong> {remediation}</p>'


def get_available_templates() -> List[str]:
    """Get list of available report templates."""
    template_dir = Path(__file__).parent / "templates"
    if not template_dir.exists():
        return ["default"]
    
    templates = []
    for file in template_dir.glob("*.html"):
        templates.append(file.stem)
    
    return templates or ["default"]


def display_attack_suggestions(attack_data: Dict[str, Any]):
    """
    Display attack/exploitation suggestions in console.
    
    Args:
        attack_data: Dictionary with attack suggestions from AI
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    if not attack_data or "warning" in attack_data and "Không phát hiện" in attack_data.get("warning", ""):
        console.print("\n[dim]Không có attack suggestions (không phát hiện lỗ hổng)[/dim]")
        return
    
    # Display warning
    warning_text = attack_data.get("warning", "")
    if warning_text:
        console.print(f"\n[bold red]{warning_text}[/bold red]")
    
    # Display attack scenarios
    attack_scenarios = attack_data.get("attack_scenarios", "")
    if attack_scenarios:
        panel = Panel(
            Markdown(attack_scenarios),
            title="[bold red]🎯 ATTACK/EXPLOITATION SUGGESTIONS[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print("\n")
        console.print(panel)
        
        # Footer
        console.print(f"\n[dim]Generated by: {attack_data.get('model_used', 'AI')}[/dim]")
        console.print(f"[dim]Scan ID: {attack_data.get('scan_id', 'N/A')}[/ dim]\n")


def display_defense_suggestions(defense_data: Dict[str, Any]):
    """
    Display defense/remediation suggestions in console.
    
    Args:
        defense_data: Dictionary with defense suggestions from AI
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    if not defense_data or "warning" in defense_data and "Không phát hiện" in defense_data.get("warning", ""):
        console.print("\n[dim]Không có defense suggestions (không phát hiện lỗ hổng)[/dim]")
        return
    
    # Display remediation steps
    remediation_steps = defense_data.get("remediation_steps", "")
    if remediation_steps:
        panel = Panel(
            Markdown(remediation_steps),
            title="[bold green]🛡️  DEFENSE/REMEDIATION SUGGESTIONS[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print("\n")
        console.print(panel)
        
        # Footer
        console.print(f"\n[dim]Generated by: {defense_data.get('model_used', 'AI')}[/dim]")
        console.print(f"[dim]Scan ID: {defense_data.get('scan_id', 'N/A')}[/dim]\n")

