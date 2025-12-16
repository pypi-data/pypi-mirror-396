"""Scan commands for DUTVulnScanner CLI."""

import typer
import subprocess
import sys
import os
import json
import threading
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from dutVulnScanner.core.orchestrator import ScanOrchestrator
from dutVulnScanner.core.config import load_config

app = typer.Typer()
console = Console()

# Directory to store background scan metadata
SCAN_TRACKING_DIR = Path.home() / ".dutvulnscanner" / "background_scans"
SCAN_TRACKING_DIR.mkdir(parents=True, exist_ok=True)


def _start_daemon_monitor(pid: int, target: str, metadata_file: Path):
    """Start a background monitor process to track daemon completion and send toast."""
    import threading

    def monitor_daemon():
        """Monitor daemon process and send notification when complete."""
        import time
        import psutil

        try:
            proc = psutil.Process(pid)

            # Wait for process to complete
            proc.wait(timeout=None)  # Wait indefinitely

            # Process completed, now wait a bit for file operations to finish
            time.sleep(2)

            # Check if scan actually completed by looking for report file or manifest
            scan_completed = False
            output_dir = None

            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    output_dir = metadata.get("output_dir")
            except Exception:
                pass

            # Check for manifest file (sign of completion)
            if output_dir:
                manifest_path = Path(output_dir) / "scan_manifest.json"
                for attempt in range(30):  # Wait up to 30 seconds for manifest
                    if manifest_path.exists():
                        scan_completed = True
                        break
                    time.sleep(1)

            # If still not completed, check log file for completion markers
            if not scan_completed:
                try:
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                        log_file = metadata.get("log_file")

                    if log_file:
                        for attempt in range(30):  # Wait up to 30 seconds
                            try:
                                with open(log_file, "r") as f:
                                    log_content = f.read()
                                    # Look for completion markers
                                    if any(
                                        marker in log_content
                                        for marker in [
                                            "Scan completed",
                                            "PDF notification sent to Discord",
                                            "Scan tracked at",
                                        ]
                                    ):
                                        scan_completed = True
                                        break
                            except Exception:
                                pass
                            time.sleep(1)
                except Exception:
                    pass

            # Process completed and scan is done, send toast notification
            if scan_completed:
                try:
                    from dutVulnScanner.notification.manager import NotificationManager

                    notif_manager = NotificationManager()
                    notif_manager.add_toast_notification("DUTVulnScanner", timeout=10)
                    notif_manager.send_toast(
                        title="Scan Complete", message=f"✓ Scan of {target} completed successfully"
                    )
                except Exception:
                    # Silently fail if toast can't be sent
                    pass

            # Update metadata
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                metadata["status"] = "completed"
                metadata["completion_time"] = datetime.now().isoformat()
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)
            except Exception:
                pass

        except psutil.NoSuchProcess:
            pass
        except Exception:
            pass

    # Start monitor in daemon thread (won't block main process)
    monitor_thread = threading.Thread(target=monitor_daemon, daemon=True)
    monitor_thread.start()


@app.command()
def run(
    target: str = typer.Argument(..., help="Target host or IP address"),
    profile: str = typer.Option("web", "--profile", "-p", help="Scan profile to use"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-d", help="Directory to save scan results and tool outputs (JSON manifest will be auto-generated)"
    ),
    tools: Optional[List[str]] = typer.Option(None, "--tool", "-t", help="Specific tools to use"),
    daemon: bool = typer.Option(False, "--daemon", help="Run scan in background daemon mode"),
    skip_check: bool = typer.Option(False, "--skip-check", help="Skip dependency check before scan"),
    generate_report: bool = typer.Option(False, "--generate-report", "-r", help="Generate AI-powered PDF report"),
    attack: bool = typer.Option(
        False, "--attack", help="Generate attack/exploitation command suggestions (requires --generate-report)"
    ),
    defense: bool = typer.Option(
        False, "--defense", help="Generate defense/remediation command suggestions (requires --generate-report)"
    ),
    upload_pdf: bool = typer.Option(
        False, "--upload-pdf", help="Upload PDF report to Firebase Storage (requires Firebase credentials)"
    ),
):
    """
    Run a vulnerability scan against a target.

    Example:
        dutVulnScanner scan run example.com --profile web --output-dir ./scan_results
        dutVulnScanner scan run example.com --profile quick --output-dir ./results
        dutVulnScanner scan run example.com --profile quick --daemon
        dutVulnScanner scan run example.com --profile web --skip-check
    """
    if daemon:
        # Run in background daemon mode
        console.print(f"[bold blue]Starting background scan against:[/bold blue] {target}")
        console.print(f"[dim]Profile: {profile} | Runner: local[/dim]")

        # Check dependencies BEFORE starting daemon (if not skipped)
        if not skip_check:
            try:
                config = load_config()
                orchestrator = ScanOrchestrator(config)
                from dutVulnScanner.core.config import load_profile
                
                profile_config = load_profile(profile)
                required_tools = tools or profile_config.get("tools", [])
                
                # Validate dependencies
                missing_tools = orchestrator._validate_dependencies(profile_config, tools)
                
                if missing_tools:
                    # Show missing tools
                    console.print(f"\n[yellow]⚠️  Missing {len(missing_tools)} tools:[/yellow]")
                    
                    from dutVulnScanner.core.tool_registry import get_tool_info
                    for tool in missing_tools:
                        tool_info = get_tool_info(tool)
                        if tool_info:
                            console.print(f"  [red]✗[/red] {tool} - {tool_info['description']}")
                    
                    console.print()
                    
                    # Ask user
                    from rich.prompt import Confirm
                    should_install = Confirm.ask("Do you want to install these tools?")
                    
                    if should_install:
                        # Install missing tools
                        success = orchestrator._install_missing_tools(missing_tools)
                        if not success:
                            console.print("[red]Failed to install some tools. Daemon cancelled.[/red]")
                            raise typer.Exit(1)
                        console.print("[green]✓ All tools installed successfully![/green]\n")
                    else:
                        console.print("[yellow]Daemon cancelled due to missing dependencies.[/yellow]")
                        raise typer.Exit(0)
            except Exception as e:
                console.print(f"[red]Error checking dependencies: {e}[/red]")
                raise typer.Exit(1)

        try:
            # Prepare command to run in background
            cmd = [sys.executable, "-m", "dutVulnScanner"]

            # Add arguments
            cmd.extend(["scan", "run", target])
            cmd.extend(["--profile", profile])
            cmd.append("--skip-check")  # Skip check in subprocess since we already checked
            if output_dir:
                cmd.extend(["--output-dir", str(output_dir)])
            if tools:
                for tool in tools:
                    cmd.extend(["--tool", tool])

            # Add report generation flags
            if generate_report:
                cmd.append("--generate-report")
            if attack:
                cmd.append("--attack")
            if defense:
                cmd.append("--defense")
            if upload_pdf:
                cmd.append("--upload-pdf")

            # Remove daemon flag to avoid infinite recursion
            # cmd is already prepared without --daemon

            console.print(f"[dim]Starting daemon process...[/dim]")
            console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")

            # Create log file for daemon process
            log_dir = Path.home() / ".dutVulnScanner" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"daemon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

            # Start process in background
            # Pass environment variables (including Discord webhook) to subprocess
            env = os.environ.copy()

            # Also load from user config directory to ensure webhook is available
            from dotenv import load_dotenv

            user_env_file = Path.home() / ".dutVulnScanner" / ".env"
            if user_env_file.exists():
                # Load user env file into current process first
                load_dotenv(user_env_file)
                # Then copy to env dict for subprocess
                env.update(os.environ)

            process = subprocess.Popen(
                cmd,
                stdout=open(log_file, "w"),
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=env,  # Pass environment to subprocess
            )

            console.print(f"[bold green]✓[/bold green] Scan started in background!")
            console.print(f"[dim]Process ID: {process.pid}[/dim]")
            console.print(f"[dim]Log file: {log_file}[/dim]")

            # Save process metadata for tracking
            scan_metadata = {
                "pid": process.pid,
                "target": target,
                "profile": profile,
                "output_dir": str(output_dir) if output_dir else None,
                "tools": tools or [],
                "start_time": datetime.now().isoformat(),
                "status": "running",
                "command": " ".join(cmd),
                "log_file": str(log_file),
            }

            metadata_file = SCAN_TRACKING_DIR / f"scan_{process.pid}.json"
            with open(metadata_file, "w") as f:
                json.dump(scan_metadata, f, indent=2)

            console.print(f"[dim]Scan tracked at: {metadata_file}[/dim]")
            console.print(f"[dim]Log file: {log_file}[/dim]")
            console.print(f"[dim]Use 'dutVulnScanner scan status' to check progress[/dim]")
            console.print(f"[dim]Results will be saved to: {output_dir or 'scan_results/'}[/dim]")

            # Wait a moment and check if process is still running
            import time

            time.sleep(1)
            if process.poll() is None:
                console.print(f"[dim]Process {process.pid} is running[/dim]")

                # Start a background monitor to send toast notification when scan completes
                _start_daemon_monitor(process.pid, target, metadata_file)
            else:
                console.print(f"[yellow]Warning: Process {process.pid} exited with code {process.returncode}[/yellow]")

        except Exception as e:
            console.print(f"[bold red]Error starting daemon:[/bold red] {str(e)}")
            raise typer.Exit(1)

    else:
        # Run in foreground mode (original behavior)
        console.print(f"[bold blue]Starting scan against:[/bold blue] {target}")
        console.print(f"[dim]Profile: {profile} | Runner: local[/dim]")

        try:
            config = load_config()
            orchestrator = ScanOrchestrator(config)
            
            # Check dependencies BEFORE starting progress bar (if not skipped)
            if not skip_check:
                from dutVulnScanner.core.config import load_profile
                profile_config = load_profile(profile)
                required_tools = tools or profile_config.get("tools", [])
                
                # Validate dependencies outside of progress context
                missing_tools = orchestrator._validate_dependencies(profile_config, tools)
                
                if missing_tools:
                    # Show missing tools
                    console.print(f"\n[yellow]⚠️  Missing {len(missing_tools)} tools:[/yellow]")
                    
                    from dutVulnScanner.core.tool_registry import get_tool_info
                    for tool in missing_tools:
                        tool_info = get_tool_info(tool)
                        if tool_info:
                            console.print(f"  [red]✗[/red] {tool} - {tool_info['description']}")
                    
                    console.print()
                    
                    # Ask user (outside progress context - prompt is visible)
                    from rich.prompt import Confirm
                    should_install = Confirm.ask("Do you want to install these tools?")
                    
                    if should_install:
                        # Install missing tools
                        success = orchestrator._install_missing_tools(missing_tools)
                        if not success:
                            console.print("[red]Failed to install some tools. Scan cancelled.[/red]")
                            raise typer.Exit(1)
                        console.print("[green]✓ All tools installed successfully![/green]\n")
                    else:
                        console.print("[yellow]Scan cancelled due to missing dependencies.[/yellow]")
                        raise typer.Exit(0)

            # Now start the scan with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Preparing scan...", total=None)

                def update_progress(tool_name: str, status: str):
                    """Update progress display."""
                    if status == "running":
                        progress.update(task, description=f"[cyan]Running {tool_name}...[/cyan]")
                    elif status == "completed":
                        progress.update(task, description=f"[green]✓ {tool_name} completed[/green]")
                    elif status == "failed":
                        progress.update(task, description=f"[red]✗ {tool_name} failed[/red]")

                results = orchestrator.run_scan(
                    target=target,
                    profile=profile,
                    runner="local",
                    tools=tools,
                    runner_config=None,
                    progress_callback=update_progress,
                    output_dir=output_dir,  # Pass output_dir to save individual tool outputs
                    skip_dependency_check=True,  # Already checked above, skip in orchestrator
                )

                progress.update(task, description="[green]✓ Scan completed[/green]", completed=True)

            console.print(f"[bold green]✓[/bold green] Scan completed!")
            console.print(f"Found {len(results.get('vulnerabilities', []))} vulnerabilities")

            # Send basic scan completion toast notification
            try:
                from dutVulnScanner.notification.manager import NotificationManager

                notif_manager = NotificationManager()
                notif_manager.add_toast_notification("DUTVulnScanner", timeout=4)
                notif_manager.send_toast(
                    title="✓ Scan Complete",
                    message=f"{target} - {len(results.get('vulnerabilities', []))} vulnerabilities found",
                )
            except Exception:
                # Silently fail if toast can't be sent
                pass

            # Show output directory
            if results.get("output_directory"):
                console.print(f"[cyan]Results saved to: {results['output_directory']}[/cyan]")
                console.print(f"[dim]→ scan_manifest.json (main results)[/dim]")
                console.print(f"[dim]→ individual tool outputs[/dim]")
            else:
                console.print(f"[yellow]Tip: Use --output-dir to save results[/yellow]")

            # Generate AI-powered PDF report if requested
            if generate_report:
                # Validate attack/defense flags
                if (attack or defense) and not generate_report:
                    console.print("[yellow]⚠ --attack and --defense require --generate-report flag[/yellow]")
                    attack = False
                    defense = False

                # Show warning for attack mode
                if attack:
                    console.print("\n[bold red]  CẢNH BÁO: CHẾ ĐỘ TẤN CÔNG[/bold red]")
                    console.print("[yellow]Các lệnh attack chỉ được sử dụng khi có sự cho phép bằng văn bản.[/yellow]")
                    console.print("[dim]Việc sử dụng trái phép có thể vi phạm pháp luật.\n[/dim]")

                try:
                    from dutVulnScanner.reporting.ai_summarizer import AISummarizer, AIAnalysisError
                    from dutVulnScanner.reporting.pdf_generator import create_pdf_report

                    console.print("\n[cyan]Generating AI-powered report...[/cyan]")

                    # Generate AI summary
                    ai_summary = None
                    attack_suggestions = None
                    defense_suggestions = None

                    try:
                        summarizer = AISummarizer()

                        # Generate main summary
                        console.print("[dim]→ Analyzing results with AI...[/dim]")
                        ai_summary = summarizer.generate_summary(results)
                        console.print("[green]✓ AI analysis completed[/green]")

                        # Generate attack suggestions if requested
                        if attack:
                            console.print("[dim]→ Generating attack suggestions...[/dim]")
                            attack_suggestions = summarizer.generate_attack_suggestions(results)
                            console.print("[green]✓ Attack suggestions generated[/green]")

                        # Generate defense suggestions if requested
                        if defense:
                            console.print("[dim]→ Generating defense suggestions...[/dim]")
                            defense_suggestions = summarizer.generate_defense_suggestions(results)
                            console.print("[green]✓ Defense suggestions generated[/green]")

                    except ValueError as e:
                        # API key missing
                        console.print(f"[yellow]⚠ {str(e)}[/yellow]")
                        console.print("[dim]→ Continuing without AI summary...[/dim]")
                    except AIAnalysisError as e:
                        # API call failed
                        console.print(f"[yellow]⚠ AI analysis failed: {str(e)}[/yellow]")
                        console.print("[dim]→ Continuing without AI summary...[/dim]")
                    except Exception as e:
                        console.print(f"[yellow]⚠ Unexpected error during AI analysis: {str(e)}[/yellow]")
                        console.print("[dim]→ Continuing without AI summary...[/dim]")

                    # Create PDF report (with attack/defense data if available)
                    console.print("[dim]→ Creating PDF report...[/dim]")

                    # Determine PDF output path
                    if results.get("output_directory"):
                        pdf_path = Path(results["output_directory"]) / "report.pdf"
                    else:
                        pdf_path = Path("scan_report.pdf")

                    # Add attack/defense suggestions to results if generated
                    if attack_suggestions:
                        results["attack_suggestions"] = attack_suggestions
                    if defense_suggestions:
                        results["defense_suggestions"] = defense_suggestions

                    create_pdf_report(pdf_path, results, ai_summary)
                    console.print(f"[bold green]✓ PDF report generated:[/bold green] {pdf_path}")

                    # Upload PDF to Firebase Storage if requested
                    if upload_pdf:
                        try:
                            # Check if Firebase credentials are configured
                            firebase_creds = os.getenv("FIREBASE_CREDENTIALS_PATH")
                            if not firebase_creds:
                                console.print("[yellow]⚠ Firebase credentials not configured[/yellow]")
                                console.print("[dim]Set FIREBASE_CREDENTIALS_PATH in ~/.dutVulnScanner/.env[/dim]")
                                console.print(
                                    "[dim]Or create Firebase credentials: https://console.firebase.google.com[/dim]"
                                )
                            else:
                                from dutVulnScanner.storage.firebase_uploader import (
                                    upload_pdf_to_firebase,
                                    FirebaseUploadError,
                                )

                                console.print("\n[cyan]Uploading PDF to Firebase Storage...[/cyan]")
                                console.print("[dim]→ Initializing Firebase...[/dim]")

                                # Upload PDF
                                pdf_url = upload_pdf_to_firebase(
                                    pdf_path=pdf_path, scan_id=results.get("scan_id", "unknown")
                                )

                                console.print(f"[green]✓ PDF uploaded successfully[/green]")
                                console.print(f"[bold cyan]📎 Public URL:[/bold cyan] {pdf_url}")

                                # Update scan_manifest.json with PDF URL
                                results["report_pdf"] = pdf_url

                                # Save updated manifest
                                manifest_path = Path(results["output_directory"]) / "scan_manifest.json"
                                if manifest_path.exists():
                                    with open(manifest_path, "w") as f:
                                        json.dump(results, f, indent=2)
                                    console.print(f"[dim]→ URL saved to scan_manifest.json[/dim]")

                        except FirebaseUploadError as e:
                            console.print(f"[yellow]⚠ Firebase upload failed: {str(e)}[/yellow]")
                            console.print("[dim]PDF is still saved locally[/dim]")
                        except ImportError:
                            console.print("[yellow]⚠ Firebase SDK not installed[/yellow]")
                            console.print("[dim]Install with: pip install firebase-admin[/dim]")
                        except Exception as e:
                            console.print(f"[yellow]⚠ Unexpected error during upload: {str(e)}[/yellow]")

                    # Save PDF path to results
                    if not upload_pdf or "report_pdf" not in results:
                        results["report_pdf"] = str(pdf_path.absolute())

                    # Update scan manifest with PDF path
                    if results.get("output_directory"):
                        manifest_path = Path(results["output_directory"]) / "scan_manifest.json"
                        with open(manifest_path, "w") as f:
                            json.dump(results, f, indent=2)
                        console.print(f"[dim]Updated scan manifest with report path[/dim]")

                    # Send PDF completion notification to Discord
                    try:
                        from dutVulnScanner.notification import NotificationManager
                        from dotenv import load_dotenv

                        user_env_file = Path.home() / ".dutVulnScanner" / ".env"
                        if user_env_file.exists():
                            load_dotenv(user_env_file)

                        discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
                        if discord_webhook:
                            notif_manager = NotificationManager()
                            notif_manager.add_discord_notification(discord_webhook)

                            # Use Firebase URL if available (after upload), otherwise use local path
                            pdf_display_path = results.get("report_pdf", str(pdf_path.absolute()))

                            notif_manager.send_pdf_report_notification(
                                target=target, pdf_path=pdf_display_path, creation_time=datetime.now().isoformat()
                            )
                            console.print(f"[dim]✓ PDF notification sent to Discord[/dim]")

                            # Send Discord notification toast
                            try:
                                notif_manager.add_toast_notification("DUTVulnScanner", timeout=6)
                                notif_manager.send_toast(
                                    title="📨 Discord Notification Sent", message=f"Report sent successfully"
                                )
                            except Exception:
                                pass
                    except Exception as e:
                        console.print(f"[dim]⚠ Failed to send PDF notification: {e}[/dim]")

                    # Display attack/defense suggestions in console if generated
                    if attack_suggestions:
                        from dutVulnScanner.reporting.builder import display_attack_suggestions

                        display_attack_suggestions(attack_suggestions)

                    if defense_suggestions:
                        from dutVulnScanner.reporting.builder import display_defense_suggestions

                        display_defense_suggestions(defense_suggestions)

                except ImportError as e:
                    console.print(f"[red]✗ Missing dependencies for report generation:[/red] {str(e)}")
                    console.print("[dim]Install with: pip install google-generativeai reportlab[/dim]")
                except Exception as e:
                    console.print(f"[red]✗ Failed to generate report:[/red] {str(e)}")
                    console.print("[dim]Scan results are still saved in JSON format[/dim]")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(1)


@app.command()
def list_tools():
    """List all available scanning tools."""
    from dutVulnScanner.plugins import AVAILABLE_ADAPTERS

    console.print("[bold]Available Scanning Tools:[/bold]")
    for name, adapter in AVAILABLE_ADAPTERS.items():
        console.print(f"  • {name}: {adapter.description}")


@app.command()
def status():
    """Check status of background scan processes."""
    console.print("[bold]Background Scan Status[/bold]\n")

    try:
        # Get all tracked scans
        scan_files = list(SCAN_TRACKING_DIR.glob("scan_*.json"))

        if not scan_files:
            console.print("[dim]No background scans found[/dim]")
            console.print(f"[dim]Tracking directory: {SCAN_TRACKING_DIR}[/dim]")
            return

        from rich.table import Table
        import psutil

        table = Table(show_header=True, title=f"Found {len(scan_files)} tracked scan(s)")
        table.add_column("PID", style="cyan", width=8)
        table.add_column("Target", style="green", width=25)
        table.add_column("Profile", style="yellow", width=12)
        table.add_column("Status", style="magenta", width=12)
        table.add_column("Started", style="blue", width=20)
        table.add_column("Output", style="white", width=30)

        active_count = 0
        for scan_file in sorted(scan_files, key=lambda f: f.stat().st_mtime, reverse=True):
            try:
                with open(scan_file) as f:
                    metadata = json.load(f)

                pid = metadata["pid"]
                target = metadata["target"]
                profile = metadata["profile"]
                start_time = metadata["start_time"]
                output_location = metadata.get("output_dir") or metadata.get("output") or "N/A"

                # Check if process is still running
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        status = "[green]●[/green] Running"
                        active_count += 1
                    else:
                        status = "[red]●[/red] Stopped"
                        # Update metadata
                        metadata["status"] = "stopped"
                        with open(scan_file, "w") as f:
                            json.dump(metadata, f, indent=2)
                except psutil.NoSuchProcess:
                    status = "[yellow]●[/yellow] Completed"
                    # Update metadata
                    metadata["status"] = "completed"
                    with open(scan_file, "w") as f:
                        json.dump(metadata, f, indent=2)

                # Format start time
                try:
                    dt = datetime.fromisoformat(start_time)
                    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_str = start_time[:19]

                # Truncate long paths
                if len(output_location) > 28:
                    output_location = "..." + output_location[-25:]

                table.add_row(
                    str(pid),
                    target[:23] + "..." if len(target) > 25 else target,
                    profile,
                    status,
                    time_str,
                    output_location,
                )

            except Exception as e:
                console.print(f"[dim]Error reading {scan_file.name}: {e}[/dim]")
                continue

        console.print(table)
        console.print(f"\n[dim]Active scans: {active_count} | Total tracked: {len(scan_files)}[/dim]")
        console.print(f"[dim]Tracking directory: {SCAN_TRACKING_DIR}[/dim]")

        # Suggest cleanup if there are completed scans
        completed = len(scan_files) - active_count
        if completed > 0:
            console.print(f"\n[yellow]Tip: Use 'dutVulnScanner scan cleanup' to remove completed scan records[/yellow]")

    except ImportError:
        console.print("[red]psutil not available. Install with: pip install psutil[/red]")
    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")


@app.command()
def cleanup(
    all: bool = typer.Option(False, "--all", "-a", help="Remove all scan records including running ones"),
):
    """Clean up completed background scan records."""
    try:
        scan_files = list(SCAN_TRACKING_DIR.glob("scan_*.json"))

        if not scan_files:
            console.print("[dim]No scan records to clean up[/dim]")
            return

        import psutil

        removed_count = 0
        kept_count = 0

        for scan_file in scan_files:
            try:
                with open(scan_file) as f:
                    metadata = json.load(f)

                pid = metadata["pid"]

                # Check if process is still running
                try:
                    proc = psutil.Process(pid)
                    is_running = proc.is_running()
                except psutil.NoSuchProcess:
                    is_running = False

                # Remove if completed or if --all flag is set
                if not is_running or all:
                    scan_file.unlink()
                    removed_count += 1
                    status = "running" if is_running else "completed"
                    console.print(f"[dim]Removed {status} scan: PID {pid} - {metadata['target']}[/dim]")
                else:
                    kept_count += 1

            except Exception as e:
                console.print(f"[yellow]Warning: Could not process {scan_file.name}: {e}[/yellow]")
                continue

        console.print(f"\n[green]✓[/green] Cleaned up {removed_count} scan record(s)")
        if kept_count > 0:
            console.print(f"[dim]Kept {kept_count} active scan(s). Use --all to remove all records.[/dim]")

    except ImportError:
        console.print("[red]psutil not available. Install with: pip install psutil[/red]")
    except Exception as e:
        console.print(f"[red]Error during cleanup: {e}[/red]")


@app.command()
def kill(
    pid: int = typer.Argument(..., help="Process ID of the scan to kill"),
):
    """Kill a running background scan by PID."""
    try:
        import psutil

        # Find the scan metadata file
        metadata_file = SCAN_TRACKING_DIR / f"scan_{pid}.json"

        if not metadata_file.exists():
            console.print(f"[yellow]No tracked scan found with PID {pid}[/yellow]")
            console.print(f"[dim]Use 'dutVulnScanner scan status' to see tracked scans[/dim]")
            return

        # Load metadata
        with open(metadata_file) as f:
            metadata = json.load(f)

        # Try to kill the process
        try:
            proc = psutil.Process(pid)
            proc.terminate()  # Send SIGTERM

            # Wait for process to terminate
            import time

            time.sleep(1)

            if proc.is_running():
                console.print(f"[yellow]Process {pid} did not terminate, forcing kill...[/yellow]")
                proc.kill()  # Send SIGKILL
                time.sleep(0.5)

            console.print(f"[green]✓[/green] Killed scan: {metadata['target']} (PID {pid})")

            # Update metadata
            metadata["status"] = "killed"
            metadata["killed_time"] = datetime.now().isoformat()
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

        except psutil.NoSuchProcess:
            console.print(f"[yellow]Process {pid} is not running (already completed)[/yellow]")
            # Update metadata
            metadata["status"] = "completed"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

    except ImportError:
        console.print("[red]psutil not available. Install with: pip install psutil[/red]")
    except Exception as e:
        console.print(f"[red]Error killing process: {e}[/red]")


@app.command()
def validate(
    profile: str = typer.Argument(..., help="Profile name to validate"),
):
    """Validate a scan profile configuration."""
    from dutVulnScanner.core.schema import validate_profile

    try:
        is_valid, errors = validate_profile(profile)
        if is_valid:
            console.print(f"[bold green]✓[/bold green] Profile '{profile}' is valid")
        else:
            console.print(f"[bold red]✗[/bold red] Profile '{profile}' has errors:")
            for error in errors:
                console.print(f"  • {error}")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
