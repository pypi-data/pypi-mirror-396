"""Interactive shell mode for dutVulnScanner."""

import re
import ipaddress
import subprocess
import sys
import os
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from dutVulnScanner.core.config import load_profile, get_profiles_dir
from dutVulnScanner.core.orchestrator import ScanOrchestrator
from dutVulnScanner.core.config import get_default_config

console = Console()


class InteractiveShell:
    """Interactive shell for dutVulnScanner."""

    def __init__(self):
        self.target = None
        self.profile = None
        self.output = None
        self.daemon = False
        self.config = get_default_config()
        self.running = True

    @staticmethod
    def validate_target(target: str) -> tuple[bool, str]:
        """
        Validate target domain/IP address.

        Args:
            target: Target string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not target or len(target.strip()) == 0:
            return False, "Target cannot be empty"

        target = target.strip()

        # Check for invalid characters
        if any(char in target for char in [" ", "\t", "\n", "\r"]):
            return False, "Target cannot contain whitespace"

        # Try to validate as IP address
        try:
            ipaddress.ip_address(target)
            return True, ""
        except ValueError:
            pass

        # Validate as domain name
        # Domain must have at least one dot (e.g., example.com) unless it's localhost
        if target.lower() == "localhost":
            return True, ""

        if "." not in target:
            return False, "Domain must contain at least one dot (e.g., example.com)"

        # Basic domain regex: alphanumeric, dots, hyphens, max 253 chars
        domain_pattern = (
            r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
        )

        if len(target) > 253:
            return False, "Domain name too long (max 253 characters)"

        if not re.match(domain_pattern, target):
            return False, "Invalid domain name or IP address format"

        # Check for common mistakes
        if target.startswith(".") or target.endswith("."):
            return False, "Domain cannot start or end with a dot"

        if ".." in target:
            return False, "Domain cannot contain consecutive dots"

        # Validate TLD (Top Level Domain) - must be at least 2 characters
        parts = target.split(".")
        tld = parts[-1]

        if len(tld) < 2:
            return False, "Top-level domain must be at least 2 characters"

        if not tld.isalpha():
            return False, "Top-level domain must contain only letters"

        return True, ""

    @staticmethod
    def validate_profile(profile_name: str) -> tuple[bool, str]:
        """
        Validate profile name exists.

        Args:
            profile_name: Profile name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not profile_name or len(profile_name.strip()) == 0:
            return False, "Profile name cannot be empty"

        profile_name = profile_name.strip()

        # Check if profile file exists
        profiles_dir = get_profiles_dir()
        profile_path = profiles_dir / f"{profile_name}.yaml"

        if not profile_path.exists():
            # Get available profiles for suggestion
            available = [p.stem for p in profiles_dir.glob("*.yaml")]
            if available:
                suggestions = ", ".join(sorted(available)[:5])
                return False, f"Profile '{profile_name}' not found. Available: {suggestions}"
            return False, f"Profile '{profile_name}' not found"

        # Try to load and validate structure
        try:
            profile_data = load_profile(profile_name)
            if "tools" not in profile_data or not profile_data["tools"]:
                return False, f"Profile '{profile_name}' has no tools configured"
            return True, ""
        except Exception as e:
            return False, f"Profile '{profile_name}' is invalid: {str(e)}"

    def show_banner(self):
        """Display welcome banner."""
        from rich.panel import Panel
        from rich.text import Text

        # ASCII Art Logo
        logo = r"""[bold cyan]                                                                                                                                                                                
  _____  _    _ _______    __      ___    _ _      _   _     _____  _____          _   _ _   _ ______ _____  
 |  __ \| |  | |__   __|   \ \    / / |  | | |    | \ | |   / ____|/ ____|   /\   | \ | | \ | |  ____|  __ \ 
 | |  | | |  | |  | |       \ \  / /| |  | | |    |  \| |  | (___ | |       /  \  |  \| |  \| | |__  | |__) |
 | |  | | |  | |  | |        \ \/ / | |  | | |    | . ` |   \___ \| |      / /\ \ | . ` | . ` |  __| |  _  / 
 | |__| | |__| |  | |         \  /  | |__| | |____| |\  |   ____) | |____ / ____ \| |\  | |\  | |____| | \ \ 
 |_____/ \____/   |_|          \/    \____/|______|_| \_|  |_____/ \_____/_/    \_\_| \_|_| \_|______|_|  \_\
                                                                                                                                                 
[/bold cyan][bold white]                    Interactive Security Scanner v1.0[/bold white]
        """

        console.print(logo)

        # Quick Start Panel
        quick_start = Text()
        quick_start.append("Quick Start:\n", style="bold yellow")
        quick_start.append("  1. ", style="dim")
        quick_start.append("set target example.com", style="cyan")
        quick_start.append("\n  2. ", style="dim")
        quick_start.append("set profile quick", style="cyan")
        quick_start.append("\n  3. ", style="dim")
        quick_start.append("set daemon true", style="cyan")
        quick_start.append(" (optional - for background)", style="dim")
        quick_start.append("\n  4. ", style="dim")
        quick_start.append("scan", style="cyan")
        quick_start.append("\n\n", style="dim")
        quick_start.append("Type ", style="dim")
        quick_start.append("help", style="bold green")
        quick_start.append(" for all commands | Type ", style="dim")
        quick_start.append("exit", style="bold red")
        quick_start.append(" to quit", style="dim")

        console.print(Panel(quick_start, border_style="cyan", padding=(1, 2)))
        console.print()

    def show_help(self):
        """Display help information."""
        table = Table(title="Available Commands", show_header=True)
        table.add_column("Command", style="cyan", width=20)
        table.add_column("Description", style="white")
        table.add_column("Example", style="dim")

        commands = [
            ("help", "Show this help message", "help"),
            ("set target <value>", "Set target host/IP", "set target example.com"),
            ("set profile <name>", "Set scan profile", "set profile web"),
            ("set output <file>", "Set output file", "set output results.json"),
            ("set daemon <true/false>", "Enable/disable background mode", "set daemon true"),
            ("show target", "Show current target", "show target"),
            ("show profile", "Show current profile", "show profile"),
            ("show daemon", "Show daemon mode status", "show daemon"),
            ("show options", "Show all current options", "show options"),
            ("profiles", "List all available profiles", "profiles"),
            ("tools", "List all available tools", "tools"),
            ("status", "Check background scan status", "status"),
            ("scan", "Run scan with current settings", "scan"),
            ("run", "Alias for scan", "run"),
            ("clear", "Clear the screen", "clear"),
            ("exit / quit", "Exit interactive shell", "exit"),
        ]

        for cmd, desc, example in commands:
            table.add_row(cmd, desc, example)

        console.print(table)

    def show_options(self):
        """Display current configuration."""
        table = Table(title="Current Options", show_header=True)
        table.add_column("Option", style="cyan", width=15)
        table.add_column("Value", style="green")

        table.add_row("Target", self.target or "[dim]Not set[/dim]")
        table.add_row("Profile", self.profile or "[dim]Not set[/dim]")
        table.add_row("Output", self.output or "[dim]Not set[/dim]")
        table.add_row("Daemon Mode", "[green]Enabled[/green]" if self.daemon else "[dim]Disabled[/dim]")

        console.print(table)

    def show_profile_details(self, profile_name: str):
        """Display detailed profile configuration and pipeline."""
        try:
            profile_data = load_profile(profile_name)

            # Header
            console.print(f"\n[bold cyan]Profile: {profile_name}[/bold cyan]")
            console.print(f"[dim]{profile_data.get('description', 'No description')}[/dim]\n")

            # Metadata
            metadata = profile_data.get("metadata", {})
            if metadata:
                meta_table = Table(show_header=False, box=None)
                meta_table.add_column("Key", style="yellow")
                meta_table.add_column("Value", style="white")

                if "estimated_duration" in metadata:
                    meta_table.add_row("Duration:", metadata["estimated_duration"])
                if "risk_level" in metadata:
                    risk = metadata["risk_level"]
                    risk_color = "red" if "Authorization" in risk or "⚠️" in risk else "green"
                    meta_table.add_row("Risk Level:", f"[{risk_color}]{risk}[/{risk_color}]")

                console.print(meta_table)
                console.print()

            # Tools Pipeline
            tools = profile_data.get("tools", [])
            if tools:
                console.print(f"[bold yellow]Scan Pipeline ({len(tools)} tools):[/bold yellow]")
                for idx, tool in enumerate(tools, 1):
                    console.print(f"  {idx}. [green]{tool}[/green]")
                console.print()

            # Tool Configurations and Command Preview
            tool_configs = profile_data.get("tool_configs", {})
            if tool_configs:
                console.print("[bold yellow]Tool Configurations & Command Preview:[/bold yellow]")

                # Import adapters to build commands
                from dutVulnScanner.plugins import AVAILABLE_ADAPTERS

                for tool_name, config in tool_configs.items():
                    console.print(f"\n  [cyan]{tool_name}:[/cyan]")

                    # Show configuration
                    if isinstance(config, dict):
                        for key, value in config.items():
                            # Format value nicely
                            if isinstance(value, list):
                                value_str = ", ".join(str(v) for v in value)
                            elif value is None:
                                value_str = "[dim]default[/dim]"
                            else:
                                value_str = str(value)
                            console.print(f"    {key}: [white]{value_str}[/white]")
                    else:
                        console.print(f"    [white]{config}[/white]")

                    # Show command preview
                    if tool_name in AVAILABLE_ADAPTERS:
                        try:
                            adapter_class = AVAILABLE_ADAPTERS[tool_name]
                            adapter = adapter_class(self.config)

                            # Use example.com as placeholder target
                            target_example = self.target or "example.com"
                            command = adapter.build_command(target_example, config if isinstance(config, dict) else {})

                            console.print(f"    [dim]Command:[/dim] [yellow]{command}[/yellow]")
                        except Exception as e:
                            console.print(f"    [dim]Command: (unable to generate - {type(e).__name__})[/dim]")

                console.print()
            elif tools:
                # If no tool_configs but has tools, still show command preview
                console.print("[bold yellow]Command Preview:[/bold yellow]")
                from dutVulnScanner.plugins import AVAILABLE_ADAPTERS

                for tool_name in tools:
                    if tool_name in AVAILABLE_ADAPTERS:
                        try:
                            adapter_class = AVAILABLE_ADAPTERS[tool_name]
                            adapter = adapter_class(self.config)
                            target_example = self.target or "example.com"
                            command = adapter.build_command(target_example, {})
                            console.print(f"\n  [cyan]{tool_name}:[/cyan]")
                            console.print(f"    [yellow]{command}[/yellow]")
                        except Exception:
                            pass
                console.print()

        except FileNotFoundError:
            console.print(f"[red]✗ Profile '{profile_name}' not found[/red]")
            console.print("[dim]Use 'profiles' to see available profiles[/dim]")
        except Exception as e:
            console.print(f"[red]Error loading profile: {e}[/red]")

    def list_profiles(self):
        """List available profiles."""
        profiles_dir = get_profiles_dir()
        profiles = list(profiles_dir.glob("*.yaml"))

        table = Table(title="Available Profiles", show_header=True)
        table.add_column("Profile", style="cyan", width=20)
        table.add_column("Description", style="white", width=40)
        table.add_column("Duration", style="yellow", width=15)
        table.add_column("Risk Level", style="magenta", width=25)

        # Load and categorize profiles
        safe_profiles = []
        auth_required_profiles = []

        for profile_path in profiles:
            name = profile_path.stem
            try:
                profile_data = load_profile(name)
                description = profile_data.get("description", "")
                metadata = profile_data.get("metadata", {})
                duration = metadata.get("estimated_duration", "N/A")
                risk = metadata.get("risk_level", "Unknown")

                profile_info = {"name": name, "description": description, "duration": duration, "risk": risk}

                # Categorize by risk level
                if "Authorization" in risk or "⚠️" in risk:
                    auth_required_profiles.append(profile_info)
                else:
                    safe_profiles.append(profile_info)
            except Exception as e:
                safe_profiles.append(
                    {"name": name, "description": f"[red]Error: {e}[/red]", "duration": "N/A", "risk": "Unknown"}
                )

        # Sort by estimated duration (extract hours/minutes for sorting)
        def extract_time_minutes(duration_str):
            """Convert duration string to minutes for sorting."""
            if "N/A" in duration_str or "Unknown" in duration_str:
                return 0
            duration_str = duration_str.lower().replace("~", "").strip()

            # Extract first number
            import re

            match = re.search(r"(\d+)", duration_str)
            if not match:
                return 0

            value = int(match.group(1))
            if "hour" in duration_str:
                return value * 60
            elif "minute" in duration_str:
                return value
            return value

        safe_profiles.sort(key=lambda p: extract_time_minutes(p["duration"]))
        auth_required_profiles.sort(key=lambda p: extract_time_minutes(p["duration"]))

        # Add safe profiles
        for profile in safe_profiles:
            risk_display = f"[green]{profile['risk']}[/green]"
            table.add_row(profile["name"], profile["description"], profile["duration"], risk_display)

        # Add separator
        if safe_profiles and auth_required_profiles:
            table.add_row("", "", "", "", end_section=True)

        # Add auth required profiles
        for profile in auth_required_profiles:
            risk_display = f"[red]{profile['risk']}[/red]"
            table.add_row(profile["name"], profile["description"], profile["duration"], risk_display)

        console.print(table)

    def list_tools(self):
        """List available scanning tools."""
        from dutVulnScanner.plugins import ADAPTERS_BY_CATEGORY
        from rich.table import Table

        table = Table(title="Available Security Tools", show_header=True)
        table.add_column("Category", style="bold cyan", width=12)
        table.add_column("Tool", style="green", width=15)
        table.add_column("Description", style="white")

        categories = list(ADAPTERS_BY_CATEGORY.items())
        for idx, (category, adapters) in enumerate(categories):
            first_in_category = True
            for name, adapter_class in adapters.items():
                try:
                    # Try to get description without full initialization
                    adapter = adapter_class(self.config)
                    desc = adapter.description
                except Exception as e:
                    # Fallback: show tool name with error indicator
                    desc = f"[dim](Error loading: {type(e).__name__})[/dim]"

                category_display = category.upper() if first_in_category else ""
                table.add_row(category_display, name, desc)
                first_in_category = False

            # Add separator line between categories (except after last category)
            if idx < len(categories) - 1:
                table.add_row("", "", "", end_section=True)

        console.print(table)

    def show_scan_status(self):
        """Check status of background scan processes."""
        try:
            import psutil
        except ImportError:
            console.print("[red]psutil not available. Install with: pip install psutil[/red]")
            return

        console.print("[bold]Background Scan Status[/bold]")

        try:
            current_pid = os.getpid()
            python_processes = []

            # Find all Python processes
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["name"] and "python" in proc.info["name"].lower():
                        cmdline = proc.info["cmdline"]
                        if cmdline and len(cmdline) > 1:
                            # Check if it's dutVulnScanner scan run
                            if "dutVulnScanner" in " ".join(cmdline) and "scan" in cmdline and "run" in cmdline:
                                python_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not python_processes:
                console.print("[dim]No background scans running[/dim]")
                return

            # Display running scans
            from rich.table import Table

            table = Table(show_header=True)
            table.add_column("PID", style="cyan", width=8)
            table.add_column("Target", style="green", width=20)
            table.add_column("Profile", style="yellow", width=12)
            table.add_column("Status", style="magenta", width=10)
            table.add_column("CPU %", style="blue", width=8)
            table.add_column("Memory", style="red", width=12)

            for proc_info in python_processes:
                pid = proc_info["pid"]
                cmdline = proc_info["cmdline"]

                # Extract target and profile from command line
                target = "unknown"
                profile = "unknown"

                try:
                    # Parse command line arguments
                    i = 0
                    while i < len(cmdline):
                        if cmdline[i] == "run" and i + 1 < len(cmdline):
                            target = cmdline[i + 1]
                        elif cmdline[i] == "--profile" and i + 1 < len(cmdline):
                            profile = cmdline[i + 1]
                        i += 1
                except:
                    pass

                # Get process status
                try:
                    proc = psutil.Process(pid)
                    status = proc.status()
                    cpu_percent = f"{proc.cpu_percent():.1f}"
                    memory_mb = f"{proc.memory_info().rss / 1024 / 1024:.1f}MB"

                    status_display = {
                        "running": "[green]Running[/green]",
                        "sleeping": "[yellow]Sleeping[/yellow]",
                        "stopped": "[red]Stopped[/red]",
                        "zombie": "[red]Zombie[/red]",
                    }.get(status, f"[dim]{status}[/dim]")

                    table.add_row(str(pid), target, profile, status_display, cpu_percent, memory_mb)

                except psutil.NoSuchProcess:
                    table.add_row(str(pid), target, profile, "[red]Terminated[/red]", "-", "-")

            console.print(table)
            console.print(f"\n[dim]Found {len(python_processes)} background scan(s)[/dim]")

        except Exception as e:
            console.print(f"[red]Error checking status: {e}[/red]")

    def run_scan(self):
        """Execute scan with current settings."""
        # Validate settings
        if not self.target:
            console.print("[red]Error: Target not set. Use 'set target <host>'[/red]")
            return

        if not self.profile:
            console.print("[yellow]Warning: Profile not set. Using 'quick' profile.[/yellow]")
            self.profile = "quick"

        # Confirm before running
        console.print(f"\n[bold]Scan Configuration:[/bold]")
        console.print(f"  Target:  [cyan]{self.target}[/cyan]")
        console.print(f"  Profile: [cyan]{self.profile}[/cyan]")
        console.print(f"  Output:  [cyan]{self.output or 'stdout'}[/cyan]")
        console.print(f"  Mode:    [cyan]{'Background' if self.daemon else 'Interactive'}[/cyan]")

        if not Confirm.ask("\nProceed with scan?", default=True):
            console.print("[yellow]Scan cancelled.[/yellow]")
            return

        if self.daemon:
            # Run in background daemon mode
            try:
                console.print("\n[bold green]Starting background scan...[/bold green]")

                # Prepare command to run in background
                cmd = [sys.executable, "-m", "dutVulnScanner.cli.commands.scan"]

                # Add arguments
                cmd.extend(["run", self.target])
                cmd.extend(["--profile", self.profile])
                if self.output:
                    cmd.extend(["--output", self.output])

                console.print(f"[dim]Starting daemon process...[/dim]")

                # Start process in background
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                )

                console.print(f"[bold green]✓[/bold green] Scan started in background!")
                console.print(f"[dim]Process ID: {process.pid}[/dim]")
                console.print(f"[dim]Use 'ps aux | grep {process.pid}' to check status[/dim]")
                console.print(f"[dim]Results will be saved to: {self.output or 'stdout'}[/dim]")

            except Exception as e:
                console.print(f"[bold red]Error starting daemon: {e}[/bold red]")
        else:
            # Run in foreground mode (original behavior)
            try:
                console.print("\n[bold green]Starting scan...[/bold green]")

                orchestrator = ScanOrchestrator(self.config)

                # Execute scan
                result = orchestrator.run_scan(target=self.target, profile=self.profile, runner="local")

                console.print("[bold green]✓ Scan completed successfully![/bold green]")

                if result and "vulnerabilities" in result:
                    vuln_count = len(result["vulnerabilities"])
                    console.print(f"\nFound [bold]{vuln_count}[/bold] findings.")

                    if self.output:
                        console.print(f"Results saved to: [cyan]{self.output}[/cyan]")

            except Exception as e:
                console.print(f"[bold red]Error during scan: {e}[/bold red]")

    def process_command(self, command: str):
        """Process user command."""
        parts = command.strip().split()

        if not parts:
            return

        cmd = parts[0].lower()

        # Help
        if cmd in ["help", "?", "h"]:
            self.show_help()

        # Set commands
        elif cmd == "set":
            # Check for --help flag
            if len(parts) >= 2 and parts[1] in ["--help", "-h", "help"]:
                console.print("\n[bold cyan]Set Command Help[/bold cyan]")
                console.print("Usage: set <option> <value>")
                console.print("\nOptions:")
                console.print("  target   - Set the target host/domain to scan")
                console.print("  profile  - Set the scanning profile to use")
                console.print("  output   - Set the output file path")
                console.print("  daemon   - Enable/disable background daemon mode (true/false)")
                console.print("\nExample:")
                console.print("  set target example.com")
                console.print("  set profile web")
                console.print("  set output results.json")
                console.print("  set daemon true")
                return

            if len(parts) < 3:
                console.print("[red]Usage: set <option> <value>[/red]")
                console.print("[dim]Type 'set --help' for more information[/dim]")
                return

            option = parts[1].lower()
            value = " ".join(parts[2:])

            # Validate input
            if value.startswith("--") or value.startswith("-"):
                console.print(f"[red]Error: Invalid value '{value}'. Did you mean 'set --help'?[/red]")
                return

            if option == "target":
                # Validate target
                is_valid, error_msg = self.validate_target(value)
                if not is_valid:
                    console.print(f"[red]✗ Invalid target: {error_msg}[/red]")
                    console.print("[dim]Target must be a valid domain name or IP address[/dim]")
                    console.print("[dim]Examples: example.com, sub.example.com, 192.168.1.1[/dim]")
                    return

                self.target = value
                console.print(f"[green]✓ Target set to: {value}[/green]")
            elif option == "profile":
                # Validate profile
                is_valid, error_msg = self.validate_profile(value)
                if not is_valid:
                    console.print(f"[red]✗ Invalid profile: {error_msg}[/red]")
                    console.print("[dim]Use 'profiles' to see available profiles[/dim]")
                    return

                self.profile = value
                console.print(f"[green]✓ Profile set to: {value}[/green]")
                console.print(f"[dim]Use 'show profile {value}' to see configuration details[/dim]")
            elif option == "output":
                self.output = value
                console.print(f"[green]✓ Output set to: {value}[/green]")
            elif option == "daemon":
                # Handle daemon mode setting
                if value.lower() in ["true", "1", "yes", "on", "enable"]:
                    self.daemon = True
                    console.print(f"[green]✓ Daemon mode enabled[/green]")
                elif value.lower() in ["false", "0", "no", "off", "disable"]:
                    self.daemon = False
                    console.print(f"[green]✓ Daemon mode disabled[/green]")
                else:
                    console.print(f"[red]Invalid daemon value: {value}[/red]")
                    console.print("[dim]Use 'true' or 'false'[/dim]")
            else:
                console.print(f"[red]Unknown option: {option}[/red]")
                console.print("[dim]Type 'set --help' for valid options[/dim]")

        # Show commands
        elif cmd == "show":
            # Check for --help flag
            if len(parts) >= 2 and parts[1] in ["--help", "-h", "help"]:
                console.print("\n[bold cyan]Show Command Help[/bold cyan]")
                console.print("Usage: show [option] [value]")
                console.print("\nOptions:")
                console.print("  target         - Display current target")
                console.print("  profile [name] - Display current profile or details of specific profile")
                console.print("  output         - Display current output path")
                console.print("  daemon         - Display current daemon mode setting")
                console.print("  options        - Display all current settings (default)")
                console.print("\nExamples:")
                console.print("  show")
                console.print("  show target")
                console.print("  show profile")
                console.print("  show profile web")
                return

            if len(parts) < 2:
                self.show_options()
                return

            option = parts[1].lower()

            if option == "target":
                console.print(f"Target: [cyan]{self.target or 'Not set'}[/cyan]")
            elif option == "profile":
                # If profile name provided, show details
                if len(parts) >= 3:
                    profile_name = parts[2]
                    self.show_profile_details(profile_name)
                else:
                    # Show current profile
                    console.print(f"Profile: [cyan]{self.profile or 'Not set'}[/cyan]")
                    if self.profile:
                        console.print("[dim]Use 'show profile <name>' to see profile details[/dim]")
            elif option == "output":
                console.print(f"Output: [cyan]{self.output or 'Not set'}[/cyan]")
            elif option == "daemon":
                status = "[green]Enabled[/green]" if self.daemon else "[dim]Disabled[/dim]"
                console.print(f"Daemon Mode: {status}")
            elif option == "options":
                self.show_options()
            else:
                console.print(f"[red]Unknown option: {option}[/red]")
                console.print("[dim]Type 'show --help' for valid options[/dim]")

        # List profiles
        elif cmd in ["profiles", "profile"]:
            if len(parts) >= 2 and parts[1] in ["--help", "-h", "help"]:
                console.print("\n[bold cyan]Profiles Command Help[/bold cyan]")
                console.print("Usage: profiles")
                console.print("\nDisplay all available scanning profiles with their descriptions,")
                console.print("estimated durations, and risk levels.")
                return
            self.list_profiles()

        # List tools
        elif cmd in ["tools", "tool"]:
            if len(parts) >= 2 and parts[1] in ["--help", "-h", "help"]:
                console.print("\n[bold cyan]Tools Command Help[/bold cyan]")
                console.print("Usage: tools")
                console.print("\nDisplay all available security scanning tools organized by category")
                console.print("(Recon, Scanners, Validators) with their descriptions.")
                return
            self.list_tools()

        # Check background scan status
        elif cmd == "status":
            if len(parts) >= 2 and parts[1] in ["--help", "-h", "help"]:
                console.print("\n[bold cyan]Status Command Help[/bold cyan]")
                console.print("Usage: status")
                console.print("\nCheck the status of running background scan processes.")
                console.print("Shows PID, target, profile, CPU usage, and memory usage.")
                return
            self.show_scan_status()

        # Run scan
        elif cmd in ["scan", "run", "start"]:
            if len(parts) >= 2 and parts[1] in ["--help", "-h", "help"]:
                console.print("\n[bold cyan]Scan Command Help[/bold cyan]")
                console.print("Usage: scan")
                console.print("\nExecute a security scan with the current settings (target and profile).")
                console.print("You will be prompted to confirm before the scan starts.")
                console.print("\nPrerequisites:")
                console.print("  - Target must be set (use: set target <host>)")
                console.print("  - Profile is optional (defaults to 'quick')")
                return
            self.run_scan()

        # Clear screen
        elif cmd == "clear":
            console.clear()
            self.show_banner()

        # Exit
        elif cmd in ["exit", "quit", "q"]:
            console.print("[yellow]Exiting interactive shell...[/yellow]")
            self.running = False

        # Unknown command
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            console.print("[dim]Type 'help' for available commands[/dim]")

    def run(self):
        """Main interactive loop."""
        self.show_banner()

        while self.running:
            try:
                # Show prompt
                command = Prompt.ask("\n[bold cyan]dutVulnScanner[/bold cyan]")

                # Process command
                self.process_command(command)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue
            except EOFError:
                break

        console.print("[bold]Goodbye! 👋[/bold]")


def start_shell():
    """Start interactive shell."""
    shell = InteractiveShell()
    shell.run()


if __name__ == "__main__":
    start_shell()
