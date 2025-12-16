"""Main CLI application entry point using Typer."""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console

from .commands import scan, profile, report, settings, doctor

app = typer.Typer(
    name="dutVulnScanner",
    help="Cross-platform vulnerability scanning tool",
    add_completion=False,
    invoke_without_command=True,
)

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-V", help="Show version information and exit"),
):
    """
    DUTVulnScanner - A comprehensive vulnerability scanning framework.

    Use 'dutVulnScanner COMMAND --help' for help on specific commands.
    """
    if version:
        # Show ASCII banner with version
        logo = r"""[bold cyan]                                                                                                                                                                                
  _____  _    _ _______    __      ___    _ _      _   _     _____  _____          _   _ _   _ ______ _____  
 |  __ \| |  | |__   __|   \ \    / / |  | | |    | \ | |   / ____|/ ____|   /\   | \ | | \ | |  ____|  __ \ 
 | |  | | |  | |  | |       \ \  / /| |  | | |    |  \| |  | (___ | |       /  \  |  \| |  \| | |__  | |__) |
 | |  | | |  | |  | |        \ \/ / | |  | | |    | . ` |   \___ \| |      / /\ \ | . ` | . ` |  __| |  _  / 
 | |__| | |__| |  | |         \  /  | |__| | |____| |\  |   ____) | |____ / ____ \| |\  | |\  | |____| | \ \ 
 |_____/ \____/   |_|          \/    \____/|______|_| \_|  |_____/ \_____/_/    \_\_| \_|_| \_|______|_|  \_\
[/bold cyan]"""
        console.print(logo)

        try:
            from dutVulnScanner import __version__

            console.print(
                f"\n[bold white]Version:[/bold white] [bold green]{__version__}[/bold green]")
        except ImportError:
            console.print(
                f"\n[bold white]Version:[/bold white] [bold yellow]Development Mode[/bold yellow]")

        console.print(
            f"[dim]Cross-platform vulnerability scanning tool[/dim]\n")
        raise typer.Exit()

    # Setup context for subcommands
    ctx.ensure_object(dict)

    # Handle case when no subcommand is provided
    if ctx.invoked_subcommand is None:
        console.print("[red]Error:[/red] No command provided.")
        console.print(
            "Use [bold]dutVulnScanner --help[/bold] for usage information.")
        console.print("\nAvailable commands:")
        console.print("  [cyan]scan[/cyan]     Run vulnerability scans")
        console.print("  [cyan]profile[/cyan]  Manage scan profiles")
        console.print("  [cyan]report[/cyan]   Generate and manage reports")
        console.print(
            "  [cyan]settings[/cyan] Configure settings (Discord, etc.)")
        console.print(
            "  [cyan]doctor[/cyan]   Check and install tool dependencies")
        raise typer.Exit(1)


# Register subcommands
app.add_typer(scan.app, name="scan", help="Run vulnerability scans")
app.add_typer(profile.app, name="profile", help="Manage scan profiles")
app.add_typer(report.app, name="report", help="Generate and manage reports")
app.add_typer(settings.app, name="settings", help="Configure settings")
app.add_typer(doctor.app, name="doctor",
              help="Check and install tool dependencies")


@app.command()
def version():
    """Display DUTVulnScanner version information."""
    from dutVulnScanner import __version__

    console.print(
        f"[bold green]DUTVulnScanner[/bold green] version {__version__}")


@app.command()
def shell():
    """Start interactive shell mode."""
    from .shell import start_shell

    start_shell()


@app.command()
def about():
    """Show the author and version information."""
    from dutVulnScanner import __version__, __authors__

    typer.echo(f"📦 dutVulnScanner v{__version__}")
    typer.echo(f"🧑‍💻 Tác giả:")
    for author in __authors__:
        typer.echo(f"   - {author['name']} <{author['email']}>")


if __name__ == "__main__":
    app()
