"""Doctor command - check and fix tool dependencies."""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from pathlib import Path

from dutVulnScanner.core.dependency_manager import DependencyManager, ToolStatus
from dutVulnScanner.core.tool_registry import (
    get_tool_info,
    get_all_tools,
    get_core_tools,
    get_recommended_tools,
    get_optional_tools,
    get_tools_by_profile,
    ToolCategory,
)
from dutVulnScanner.core.config import load_profile, get_profiles_dir

app = typer.Typer()
console = Console()


def get_status_icon(status: ToolStatus) -> str:
    """Get colored status icon."""
    if status == ToolStatus.INSTALLED:
        return "[green]✓[/green]"
    elif status == ToolStatus.NOT_FOUND:
        return "[red]✗[/red]"
    else:
        return "[yellow]?[/yellow]"


def get_category_color(category: ToolCategory) -> str:
    """Get color for category."""
    if category == ToolCategory.CORE:
        return "red"
    elif category == ToolCategory.RECOMMENDED:
        return "yellow"
    else:
        return "blue"


@app.command()
def check(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Check tools for specific profile"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """
    Check status of all tool dependencies.
    
    Example:
        dutVulnScanner doctor check
        dutVulnScanner doctor check --profile web
        dutVulnScanner doctor check --verbose
    """
    console.print("\n[bold blue]🔍 Checking tool dependencies...[/bold blue]\n")
    
    dep_manager = DependencyManager()
    
    # Determine which tools to check
    if profile:
        try:
            profile_config = load_profile(profile)
            tools_to_check = profile_config.get("tools", [])
            console.print(f"[dim]Checking tools for profile: {profile}[/dim]\n")
        except Exception as e:
            console.print(f"[red]Error loading profile '{profile}': {e}[/red]")
            raise typer.Exit(1)
    else:
        tools_to_check = get_all_tools()
    
    # Check all tools
    results = {}
    for tool in tools_to_check:
        results[tool] = dep_manager.check_tool(tool)
    
    # Create status table
    table = Table(title="Tool Dependencies Status", show_header=True, header_style="bold magenta")
    table.add_column("Tool", style="cyan", width=15)
    table.add_column("Status", width=15)
    table.add_column("Version", width=12)
    table.add_column("Category", width=12)
    
    if verbose:
        table.add_column("Path", width=40)
    
    # Add rows
    installed_count = 0
    missing_count = 0
    
    for tool_name in sorted(results.keys()):
        status_info = results[tool_name]
        tool_info = get_tool_info(tool_name)
        
        if not tool_info:
            continue
        
        status = status_info["status"]
        version = status_info.get("version", "-")
        category = tool_info["category"]
        
        status_icon = get_status_icon(status)
        category_color = get_category_color(category)
        category_text = f"[{category_color}]{category.value}[/{category_color}]"
        
        if status == ToolStatus.INSTALLED:
            installed_count += 1
            status_text = f"{status_icon} Installed"
            version_text = version or "-"
        else:
            missing_count += 1
            status_text = f"{status_icon} Missing"
            version_text = "-"
        
        if verbose:
            path = status_info.get("path", "-")
            table.add_row(tool_name, status_text, version_text, category_text, path)
        else:
            table.add_row(tool_name, status_text, version_text, category_text)
        
        # Show warning for optional tools
        if tool_info.get("warning") and status == ToolStatus.NOT_FOUND:
            pass  # We'll show warnings in summary
    
    console.print(table)
    console.print()
    
    # Summary
    total = len(results)
    if missing_count == 0:
        console.print(f"[bold green]✅ All {total} tools are installed![/bold green]")
    else:
        console.print(f"[bold yellow]⚠️  {missing_count}/{total} tools missing, {installed_count} installed[/bold yellow]")
        
        # List missing tools by category
        missing_core = [t for t in results if results[t]["status"] == ToolStatus.NOT_FOUND and get_tool_info(t)["category"] == ToolCategory.CORE]
        missing_recommended = [t for t in results if results[t]["status"] == ToolStatus.NOT_FOUND and get_tool_info(t)["category"] == ToolCategory.RECOMMENDED]
        missing_optional = [t for t in results if results[t]["status"] == ToolStatus.NOT_FOUND and get_tool_info(t)["category"] == ToolCategory.OPTIONAL]
        
        if missing_core:
            console.print(f"\n[bold red]❌ Missing core tools (required):[/bold red]")
            for tool in missing_core:
                console.print(f"   • {tool}")
        
        if missing_recommended:
            console.print(f"\n[bold yellow]⚠️  Missing recommended tools:[/bold yellow]")
            for tool in missing_recommended:
                console.print(f"   • {tool}")
        
        if missing_optional:
            console.print(f"\n[bold blue]ℹ️  Missing optional tools:[/bold blue]")
            for tool in missing_optional:
                console.print(f"   • {tool}")
        
        console.print(f"\n[dim]Run '[cyan]dutVulnScanner doctor fix[/cyan]' to install[/dim]")
    
    console.print()


@app.command()
def fix(
    tools: Optional[List[str]] = typer.Argument(None, help="Tool names to install (empty = all missing tools)"),
    all: bool = typer.Option(False, "--all", help="Install all missing tools"),
    core: bool = typer.Option(False, "--core", help="Install only core tools"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Install tools for specific profile"),
    method: Optional[str] = typer.Option(None, "--method", help="Installation method: apt, go, binary"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show only, don't install"),
):
    """
    Install missing tools.
    
    Examples:
        dutVulnScanner doctor fix                    # Interactive mode
        dutVulnScanner doctor fix nuclei             # Install specific tool
        dutVulnScanner doctor fix nuclei subfinder   # Install multiple tools
        dutVulnScanner doctor fix --all              # Install all missing
        dutVulnScanner doctor fix --core             # Install only core
        dutVulnScanner doctor fix --profile web      # Install for profile
        dutVulnScanner doctor fix --all --yes        # No confirmation
    """
    dep_manager = DependencyManager()
    
    # Determine which tools to install
    tools_to_install = []
    
    if tools:
        # Specific tools provided
        tools_to_install = tools
    elif all:
        # All missing tools
        missing = dep_manager.get_missing_tools()
        tools_to_install = missing
    elif core:
        # Only core tools
        core_tools = get_core_tools()
        missing = dep_manager.get_missing_tools(core_tools)
        tools_to_install = missing
    elif profile:
        # Tools for specific profile
        try:
            profile_config = load_profile(profile)
            profile_tools = profile_config.get("tools", [])
            missing = dep_manager.get_missing_tools(profile_tools)
            tools_to_install = missing
        except Exception as e:
            console.print(f"[red]Error loading profile '{profile}': {e}[/red]")
            raise typer.Exit(1)
    else:
        # Interactive mode - show missing and let user choose
        missing = dep_manager.get_missing_tools()
        if not missing:
            console.print("[green]✅ All tools are already installed![/green]")
            return
        
        console.print(f"\n[yellow]Found {len(missing)} missing tools:[/yellow]\n")
        
        # Show missing tools
        for tool in missing:
            tool_info = get_tool_info(tool)
            category = tool_info["category"]
            category_color = get_category_color(category)
            console.print(f"  • [cyan]{tool}[/cyan] - [{category_color}]{category.value}[/{category_color}]")
            if tool_info.get("warning"):
                console.print(f"    {tool_info['warning']}")
        
        console.print()
        
        if not Confirm.ask("Do you want to install all these tools?"):
            return
        
        tools_to_install = missing
    
    if not tools_to_install:
        console.print("[green]✅ No tools need to be installed![/green]")
        return
    
    # Dry run mode
    if dry_run:
        console.print(f"\n[yellow]📋 Dry run - would install {len(tools_to_install)} tools:[/yellow]\n")
        for tool in tools_to_install:
            tool_info = get_tool_info(tool)
            console.print(f"  • {tool} - {tool_info['description']}")
        return
    
    # Confirm installation
    if not yes and len(tools_to_install) > 1:
        console.print(f"\n[yellow]Will install {len(tools_to_install)} tools:[/yellow]")
        for tool in tools_to_install:
            console.print(f"  • {tool}")
        console.print()
        
        if not Confirm.ask("Continue?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    console.print()
    
    # Check if Go is needed and available
    needs_go = False
    for tool in tools_to_install:
        tool_info = get_tool_info(tool)
        if tool_info:
            install_info = tool_info["install_methods"].get("linux", {})
            if install_info.get("primary") == "go":
                needs_go = True
                break
    
    if needs_go and not dep_manager.check_go_installed():
        console.print("[yellow]⚠️  Some tools require Go compiler to install.[/yellow]")
        console.print("[dim]Install Go: sudo apt-get install -y golang-go[/dim]\n")
        
        if not yes and not Confirm.ask("Have you installed Go? Continue?"):
            return
    
    # Install tools
    success_count = 0
    failed_tools = []
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        console=console,
        refresh_per_second=10,
        transient=False,
    ) as progress:
        
        task = progress.add_task("[cyan]Installing tools...", total=100, completed=0)
        
        def progress_callback(action: str, value):
            """Handle progress updates, pause, and resume."""
            if action == 'update':
                progress.update(task, description=f"[cyan]{value}[/cyan]", completed=0)
            elif action == 'complete':
                # Replace with done message
                progress.update(task, description=f"[green]✓ {value}[/green]", completed=0)
            elif action == 'pause':
                # Stop progress to allow interactive prompts
                progress.stop()
            elif action == 'resume':
                # Resume progress after interactive prompt
                progress.start()
        
        for i, tool in enumerate(tools_to_install, 1):
            progress.update(task, description=f"[cyan]Installing {tool}... ({i}/{len(tools_to_install)})[/cyan]", completed=0)
            
            success, message = dep_manager.install_tool(tool, method=method, progress_callback=progress_callback)
            
            if success:
                console.print(f"  [green]✓[/green] {tool}: {message}")
                success_count += 1
            else:
                console.print(f"  [red]✗[/red] {tool}: {message}")
                failed_tools.append((tool, message))
    
    # Summary
    console.print()
    if success_count == len(tools_to_install):
        console.print(f"[bold green]✅ Successfully installed {success_count}/{len(tools_to_install)} tools![/bold green]")
    else:
        console.print(f"[bold yellow]⚠️  Installation complete: {success_count} succeeded, {len(failed_tools)} failed[/bold yellow]")
        
        if failed_tools:
            console.print("\n[bold red]Failed tools:[/bold red]")
            for tool, error in failed_tools:
                console.print(f"  • {tool}: {error}")
                console.print(f"    [dim]See instructions: dutVulnScanner doctor info {tool}[/dim]")
    
    console.print()


@app.command()
def info(
    tool: str = typer.Argument(..., help="Tool name to get information"),
):
    """
    Display detailed information about a tool.
    
    Example:
        dutVulnScanner doctor info nuclei
        dutVulnScanner doctor info nmap
    """
    dep_manager = DependencyManager()
    
    console.print()
    instructions = dep_manager.get_install_instructions(tool)
    console.print(instructions)
    console.print()
    
    # Check current status
    status = dep_manager.check_tool(tool)
    if status["status"] == ToolStatus.INSTALLED:
        console.print(f"[green]✅ Status: Installed[/green]")
        console.print(f"   Version: {status.get('version', 'Unknown')}")
        console.print(f"   Path: {status.get('path', 'Unknown')}")
    else:
        console.print(f"[red]❌ Status: Not installed[/red]")
        console.print(f"\n[dim]Install: dutVulnScanner doctor fix {tool}[/dim]")
    
    console.print()


@app.command()
def list(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category: core, recommended, optional"),
):
    """
    List all available tools in the registry.
    
    Example:
        dutVulnScanner doctor list
        dutVulnScanner doctor list --category core
    """
    console.print("\n[bold blue]📦 Available tools:[/bold blue]\n")
    
    tools = get_all_tools()
    
    # Filter by category if specified
    if category:
        if category not in ["core", "recommended", "optional"]:
            console.print(f"[red]Invalid category. Choose: core, recommended, optional[/red]")
            raise typer.Exit(1)
        
        if category == "core":
            tools = get_core_tools()
        elif category == "recommended":
            tools = get_recommended_tools()
        elif category == "optional":
            tools = get_optional_tools()
    
    # Group by type
    by_type = {"recon": [], "scanner": [], "validator": []}
    
    for tool in tools:
        tool_info = get_tool_info(tool)
        tool_type = tool_info.get("type", "other")
        if tool_type in by_type:
            by_type[tool_type].append(tool)
    
    # Display
    for tool_type, tool_list in by_type.items():
        if not tool_list:
            continue
        
        console.print(f"[bold cyan]{tool_type.upper()}:[/bold cyan]")
        for tool in sorted(tool_list):
            tool_info = get_tool_info(tool)
            category = tool_info["category"]
            category_color = get_category_color(category)
            console.print(f"  • [cyan]{tool}[/cyan] - {tool_info['description']} [{category_color}]({category.value})[/{category_color}]")
        console.print()
    
    console.print(f"[dim]Total: {len(tools)} tools[/dim]\n")


if __name__ == "__main__":
    app()
