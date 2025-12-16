"""Report generation commands."""
import typer
from pathlib import Path
from rich.console import Console

from dutVulnScanner.reporting.builder import ReportBuilder

app = typer.Typer()
console = Console()


@app.command()
def generate(
    input_file: Path = typer.Argument(..., help="Input scan results file (JSON)"),
    output_file: Path = typer.Argument(..., help="Output report file"),
    format: str = typer.Option("html", "--format", "-f", help="Report format: html, pdf, json, sarif"),
    template: str = typer.Option("default", "--template", "-t", help="Report template to use"),
):
    """
    Generate a report from scan results.
    
    Example:
        dutVulnScanner report generate results.json report.html --format html
    """
    if not input_file.exists():
        console.print(f"[red]Input file not found: {input_file}[/red]")
        raise typer.Exit(1)
    
    try:
        console.print(f"[blue]Generating {format.upper()} report...[/blue]")
        
        builder = ReportBuilder()
        builder.load_results(input_file)
        builder.generate(output_file, format=format, template=template)
        
        console.print(f"[green]✓[/green] Report generated: {output_file}")
    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input report file"),
    output_file: Path = typer.Argument(..., help="Output report file"),
    to_format: str = typer.Option(..., "--to", help="Target format: html, pdf, json, sarif"),
):
    """Convert a report from one format to another."""
    if not input_file.exists():
        console.print(f"[red]Input file not found: {input_file}[/red]")
        raise typer.Exit(1)
    
    try:
        console.print(f"[blue]Converting to {to_format.upper()}...[/blue]")
        
        builder = ReportBuilder()
        builder.load_results(input_file)
        builder.generate(output_file, format=to_format)
        
        console.print(f"[green]✓[/green] Converted to: {output_file}")
    except Exception as e:
        console.print(f"[red]Error converting report: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_templates():
    """List available report templates."""
    from dutVulnScanner.reporting.builder import get_available_templates
    
    templates = get_available_templates()
    
    console.print("[bold]Available Report Templates:[/bold]")
    for template in templates:
        console.print(f"  • {template}")
