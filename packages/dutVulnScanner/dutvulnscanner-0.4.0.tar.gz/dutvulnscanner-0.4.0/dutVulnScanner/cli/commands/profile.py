"""Profile management commands."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from dutVulnScanner.core.config import get_profiles_dir, load_profile

app = typer.Typer()
console = Console()


@app.command(name="list")
def list_profiles():
    """List all available scan profiles with details."""
    profiles_dir = get_profiles_dir()
    profiles = list(profiles_dir.glob("*.yaml"))

    if not profiles:
        console.print("[yellow]No profiles found[/yellow]")
        return

    # Categorize profiles
    safe_profiles = []
    auth_required_profiles = []

    for profile_path in profiles:
        name = profile_path.stem
        if name in ["validators", "deep_test"]:
            auth_required_profiles.append(profile_path)
        else:
            safe_profiles.append(profile_path)

    # Display safe profiles
    table = Table(title="🟢 Safe Scanning Profiles", show_lines=True)
    table.add_column("Profile", style="cyan", width=15)
    table.add_column("Description", style="white", width=40)
    table.add_column("Tools", style="green", width=30)
    table.add_column("Duration", style="yellow", width=12)

    duration_map = {
        "quick": "~10 min",
        "recon": "~30 min",
        "discovery_full": "~2 hours",
        "web": "~1 hour",
        "vuln_scan": "~3 hours",
        "infra": "~2 hours",
        "full_scan": "~6 hours",
    }

    for profile_path in sorted(safe_profiles):
        name = profile_path.stem
        try:
            profile_data = load_profile(name)
            description = profile_data.get("description", "")
            tools = ", ".join(profile_data.get("tools", [])[:3])  # Show first 3 tools
            tool_count = len(profile_data.get("tools", []))
            if tool_count > 3:
                tools += f" (+{tool_count - 3} more)"
            duration = duration_map.get(name, "~1 hour")

            table.add_row(name, description, tools, duration)
        except Exception as e:
            table.add_row(name, f"[red]Error: {e}[/red]", "", "")

    console.print(table)
    console.print()

    # Display authorization-required profiles
    if auth_required_profiles:
        auth_table = Table(title="🔴 Authorization Required Profiles", show_lines=True)
        auth_table.add_column("Profile", style="red", width=15)
        auth_table.add_column("Description", style="white", width=40)
        auth_table.add_column("Tools", style="yellow", width=30)
        auth_table.add_column("Risk", style="red bold", width=12)

        for profile_path in sorted(auth_required_profiles):
            name = profile_path.stem
            try:
                profile_data = load_profile(name)
                description = profile_data.get("description", "")
                tools = ", ".join(profile_data.get("tools", []))
                risk = "⚠️ HIGH"

                auth_table.add_row(name, description, tools, risk)
            except Exception as e:
                auth_table.add_row(name, f"[red]Error: {e}[/red]", "", "")

        console.print(auth_table)
        console.print("\n[bold red]⚠️  WARNING:[/bold red] Authorization-required profiles perform active exploitation.")
        console.print("[yellow]Only use with explicit written permission![/yellow]\n")

    # Usage examples
    console.print("[bold]Usage Examples:[/bold]")
    console.print("  dutVulnScanner scan run example.com --profile quick")
    console.print("  dutVulnScanner scan run example.com --profile discovery_full")
    console.print("  dutVulnScanner profile show recon")
    console.print()


@app.command()
def show(
    name: str = typer.Argument(..., help="Profile name to display"),
):
    """Show details of a specific profile."""
    try:
        profile_data = load_profile(name)
        console.print(f"[bold]Profile:[/bold] {name}")
        console.print(profile_data)
    except FileNotFoundError:
        console.print(f"[red]Profile '{name}' not found[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error loading profile: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Argument(..., help="New profile name"),
    template: str = typer.Option("web", "--template", "-t", help="Template to use"),
):
    """Create a new scan profile from a template."""
    profiles_dir = get_profiles_dir()
    new_profile = profiles_dir / f"{name}.yaml"

    if new_profile.exists():
        console.print(f"[red]Profile '{name}' already exists[/red]")
        raise typer.Exit(1)

    try:
        template_data = load_profile(template)
        import yaml

        with open(new_profile, "w") as f:
            yaml.safe_dump(template_data, f, default_flow_style=False)

        console.print(f"[green]✓[/green] Created profile '{name}' from template '{template}'")
        console.print(f"[dim]Location: {new_profile}[/dim]")
    except Exception as e:
        console.print(f"[red]Error creating profile: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(
    name: str = typer.Argument(..., help="Profile name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a scan profile."""
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{name}.yaml"

    if not profile_path.exists():
        console.print(f"[red]Profile '{name}' not found[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Delete profile '{name}'?")
        if not confirm:
            console.print("Cancelled")
            raise typer.Exit(0)

    profile_path.unlink()
    console.print(f"[green]✓[/green] Deleted profile '{name}'")
