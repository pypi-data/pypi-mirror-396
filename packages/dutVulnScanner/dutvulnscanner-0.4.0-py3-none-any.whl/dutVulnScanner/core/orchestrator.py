"""Scan orchestrator - coordinates scanning workflow."""

import uuid
import logging
import signal
import sys
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import json

from dutVulnScanner.core.schema import ScanResult, Vulnerability
from dutVulnScanner.core.correlation import CorrelationEngine
from dutVulnScanner.core.checkpoint import ScanCheckpoint


logger = logging.getLogger(__name__)


class ScanOrchestrator:
    """
    Orchestrates the complete scanning workflow.

    Responsibilities:
    - Load and validate profiles
    - Initialize appropriate runner
    - Execute adapters in sequence or parallel
    - Correlate results from multiple tools
    - Generate consolidated report
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator.

        Args:
            config: Global configuration dictionary
        """
        self.config = config
        self.correlation_engine = CorrelationEngine(config)
        self.scan_id = None
        self.checkpoint = ScanCheckpoint()
        self.interrupted = False

        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals (Ctrl+C)."""
        logger.warning("Interrupt signal received. Saving checkpoint...")
        self.interrupted = True

    def run_scan(
        self,
        target: str,
        profile: str,
        runner: str = "local",
        tools: Optional[List[str]] = None,
        runner_config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, str], None]] = None,
        output_dir: Optional[Path] = None,  # Directory to save individual tool outputs
        skip_dependency_check: bool = False,  # Skip dependency validation
    ) -> Dict[str, Any]:
        """
        Execute a vulnerability scan.

        Args:
            target: Target host/IP to scan
            profile: Profile name to use
            runner: Runner type (only 'local' is supported)
            tools: Optional list of specific tools to use (overrides profile)
            runner_config: Optional runner-specific configuration
            progress_callback: Optional callback function(tool_name: str, status: str)
            output_dir: Optional directory to save individual tool outputs
            skip_dependency_check: Skip dependency validation before scan

        Returns:
            Scan results dictionary
        """
        self.scan_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Create output directory for this scan
        if output_dir:
            scan_output_dir = Path(output_dir) / f"scan_{self.scan_id[:8]}_{start_time.strftime('%Y%m%d_%H%M%S')}"
            scan_output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Saving individual tool outputs to: {scan_output_dir}")
        else:
            scan_output_dir = None

        logger.info(f"Starting scan {self.scan_id} against {target}")

        try:
            # Load profile
            from dutVulnScanner.core.config import load_profile

            profile_config = load_profile(profile)
            
            # Validate dependencies before scan
            if not skip_dependency_check:
                logger.info("Validating tool dependencies...")
                missing_tools = self._validate_dependencies(profile_config, tools)
                
                if missing_tools:
                    # Dependencies missing - prompt user
                    from rich.console import Console
                    from rich.prompt import Confirm
                    
                    console = Console()
                    console.print(f"\n[yellow]⚠️  Missing {len(missing_tools)} tools:[/yellow]")
                    
                    for tool in missing_tools:
                        from dutVulnScanner.core.tool_registry import get_tool_info
                        tool_info = get_tool_info(tool)
                        if tool_info:
                            console.print(f"  [red]✗[/red] {tool} - {tool_info['description']}")
                    
                    console.print()
                    
                    # Ask user if they want to install
                    should_install = Confirm.ask("Do you want to install these tools?")
                    
                    if should_install:
                        # Install missing tools
                        success = self._install_missing_tools(missing_tools)
                        if not success:
                            logger.error("Failed to install some tools")
                            console.print("[red]Failed to install some tools. Scan cancelled.[/red]")
                            return self._create_error_result(
                                target, profile, start_time,
                                "Missing dependencies and installation failed"
                            )
                    else:
                        logger.warning("User declined to install dependencies")
                        console.print("[yellow]Scan cancelled due to missing dependencies.[/yellow]")
                        return self._create_error_result(
                            target, profile, start_time,
                            "Missing dependencies - user declined installation"
                        )

            # Override tools if specified
            if tools:
                profile_config["tools"] = tools

            # Initialize runner
            runner_instance = self._get_runner(runner, runner_config)

            # Execute adapters
            raw_results = self._execute_adapters(
                target=target,
                profile_config=profile_config,
                runner=runner_instance,
                progress_callback=progress_callback,
                output_dir=scan_output_dir,
            )

            # Correlate results
            vulnerabilities = self._correlate_results(raw_results)

            # Build final result
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            result = {
                "scan_id": self.scan_id,
                "target": target,
                "profile": profile,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration,
                "vulnerabilities": vulnerabilities,
                "tools_used": profile_config["tools"],
                "runner_type": runner,
                "status": "completed",
                "raw_results": raw_results,  # Include raw results from each tool
                "statistics": self._calculate_statistics(vulnerabilities),
                "output_directory": str(scan_output_dir) if scan_output_dir else None,
            }

            # Save scan manifest if output_dir exists
            if scan_output_dir:
                manifest_path = scan_output_dir / "scan_manifest.json"
                with open(manifest_path, "w") as f:
                    json.dump(result, f, indent=2)
                logger.info(f"Scan manifest saved to {manifest_path}")

            logger.info(f"Scan {self.scan_id} completed successfully")

            # Send notification after scan completion
            self._send_scan_notification(result)

            return result

        except Exception as e:
            logger.error(f"Scan {self.scan_id} failed: {str(e)}")
            raise

    def _get_runner(self, runner_type: str, runner_config: Optional[Dict[str, Any]] = None):
        """Get runner instance by type."""
        if runner_type == "local":
            from dutVulnScanner.runners.local import LocalRunner

            return LocalRunner(self.config)
        else:
            raise ValueError(f"Unknown runner type: {runner_type}. Only 'local' runner is supported.")

    def _execute_adapters(
        self,
        target: str,
        profile_config: Dict[str, Any],
        runner,
        progress_callback: Optional[Callable[[str, str], None]] = None,
        output_dir: Optional[Path] = None,
    ) -> List[Dict[str, Any]]:
        """Execute scanning adapters."""
        from dutVulnScanner.plugins import get_adapter

        tools = profile_config.get("tools", [])
        parallel = profile_config.get("parallel", True)

        results = []

        for tool_name in tools:
            logger.info(f"Executing {tool_name} adapter")

            # Notify progress
            if progress_callback:
                progress_callback(tool_name, "running")

            try:
                adapter = get_adapter(tool_name, self.config)
                tool_config = profile_config.get("tool_configs", {}).get(tool_name, {})

                result = runner.execute(adapter, target, tool_config)

                # Save individual tool output if output_dir exists
                if output_dir:
                    tool_output_file = output_dir / f"{tool_name}_output.json"
                    with open(tool_output_file, "w") as f:
                        json.dump(result, f, indent=2)
                    logger.info(f"{tool_name} output saved to {tool_output_file}")

                results.append(
                    {
                        "tool": tool_name,
                        "success": True,
                        "data": result,
                        "output_file": str(tool_output_file) if output_dir else None,
                    }
                )

                # Notify success
                if progress_callback:
                    progress_callback(tool_name, "completed")

            except Exception as e:
                logger.error(f"Adapter {tool_name} failed: {str(e)}")
                results.append(
                    {
                        "tool": tool_name,
                        "success": False,
                        "error": str(e),
                    }
                )

                # Notify failure
                if progress_callback:
                    progress_callback(tool_name, "failed")

        return results
    
    def _validate_dependencies(
        self, 
        profile_config: Dict[str, Any], 
        tools_override: Optional[List[str]] = None
    ) -> List[str]:
        """
        Validate that all required tools are installed.
        
        Args:
            profile_config: Profile configuration
            tools_override: Optional tools list override
            
        Returns:
            List of missing tool names
        """
        from dutVulnScanner.core.dependency_manager import DependencyManager
        
        # Get tools to check
        required_tools = tools_override or profile_config.get("tools", [])
        
        # Check each tool
        dep_manager = DependencyManager(self.config)
        missing = dep_manager.get_missing_tools(required_tools)
        
        return missing
    
    def _install_missing_tools(self, tools: List[str]) -> bool:
        """
        Install missing tools with user feedback.
        
        Args:
            tools: List of tool names to install
            
        Returns:
            True if all installations successful, False otherwise
        """
        from dutVulnScanner.core.dependency_manager import DependencyManager
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        console = Console()
        dep_manager = DependencyManager(self.config)
        
        console.print()
        
        success_count = 0
        failed_tools = []
        
        # Use simple progress without spinner
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            console=console,
            refresh_per_second=10,
            transient=False,
        ) as progress:
            
            # Set total to 100 to keep progress active
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
            
            for i, tool in enumerate(tools, 1):
                progress.update(task, description=f"[cyan]Installing {tool}... ({i}/{len(tools)})[/cyan]", completed=0)
                
                success, message = dep_manager.install_tool(tool, progress_callback=progress_callback)
                
                if success:
                    console.print(f"  [green]✓[/green] {tool}: {message}")
                    success_count += 1
                else:
                    console.print(f"  [red]✗[/red] {tool}: {message}")
                    failed_tools.append((tool, message))
        
        console.print()
        
        # Return True only if all succeeded
        return len(failed_tools) == 0
    
    def _create_error_result(
        self,
        target: str,
        profile: str,
        start_time: datetime,
        error_message: str,
    ) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "scan_id": self.scan_id,
            "target": target,
            "profile": profile,
            "start_time": start_time.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": error_message,
            "vulnerabilities": [],
            "tools_used": [],
            "statistics": {},
        }

    def _correlate_results(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Correlate results from multiple tools."""
        all_vulnerabilities = []

        # Extract vulnerabilities from each tool's results
        for result in raw_results:
            if result.get("success") and "data" in result:
                vulns = result["data"].get("vulnerabilities", [])
                all_vulnerabilities.extend(vulns)

        # Apply correlation
        correlated = self.correlation_engine.correlate(all_vulnerabilities)

        return correlated

    def _calculate_statistics(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from vulnerabilities."""
        stats = {
            "total": len(vulnerabilities),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            "by_tool": {},
        }

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "info").lower()
            if severity in stats["by_severity"]:
                stats["by_severity"][severity] += 1

            tool = vuln.get("detected_by", "unknown")
            stats["by_tool"][tool] = stats["by_tool"].get(tool, 0) + 1

        return stats

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save scan results to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_path}")

    def _send_scan_notification(self, result: Dict[str, Any]):
        """Send notification after scan completion."""
        try:
            from dutVulnScanner.notification import NotificationManager
            from dotenv import load_dotenv

            # Load from user's config directory
            user_env_file = Path.home() / ".dutVulnScanner" / ".env"
            if user_env_file.exists():
                load_dotenv(user_env_file)

            # Initialize notification manager
            manager = NotificationManager()

            # Add toast notification
            manager.add_toast_notification()

            # Add Discord notification if webhook is configured
            discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
            if discord_webhook:
                manager.add_discord_notification(discord_webhook)  # Prepare notification data
            target = result.get("target", "Unknown")
            stats = result.get("statistics", {})
            vuln_count = stats.get("total", 0)
            duration_seconds = result.get("duration", 0)

            # Format duration
            duration_str = self._format_duration(duration_seconds)

            # Send advanced Discord report if Discord is enabled
            if discord_webhook:
                # Get PDF report path if it exists
                pdf_path = result.get("report_pdf")

                # Prepare detailed vulnerability breakdown
                vulnerabilities_for_report = []
                by_severity = stats.get("by_severity", {})
                by_tool = stats.get("by_tool", {})

                # Get actual vulnerability details from result
                vuln_details = result.get("vulnerabilities", [])

                # Group vulnerabilities by severity for Discord report
                if vuln_details:
                    # Limit to 10 most critical vulnerabilities for Discord (to avoid too long message)
                    sorted_vulns = sorted(
                        vuln_details,
                        key=lambda v: {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(
                            v.get("severity", "info").lower(), 5
                        ),
                    )[:10]

                    for vuln in sorted_vulns:
                        severity = vuln.get("severity", "info")
                        title = vuln.get("title", "Unknown Vulnerability")
                        description = vuln.get("description", "No description available")
                        host = vuln.get("host", target)
                        port = vuln.get("port", "N/A")
                        service = vuln.get("service", "N/A")
                        detected_by = vuln.get("detected_by", "Unknown")

                        # Create detailed description for report
                        detailed_desc = f"{description}"
                        if port != "N/A":
                            detailed_desc += f"\nLocation: {host}:{port}"
                        if service != "N/A":
                            detailed_desc += f" ({service})"
                        detailed_desc += f"\nDetected by: {detected_by}"

                        vulnerabilities_for_report.append(
                            {
                                "severity": severity.capitalize(),
                                "count": 1,
                                "description": title,  # Use title as description for cleaner report
                            }
                        )
                else:
                    # If no detailed vulnerabilities, use breakdown by severity
                    for severity in ["critical", "high", "medium", "low"]:
                        count = by_severity.get(severity, 0)
                        if count > 0:
                            vulnerabilities_for_report.append(
                                {
                                    "severity": severity.capitalize(),
                                    "count": count,
                                    "description": f"{severity.capitalize()} severity issues",
                                }
                            )

                # Prepare enhanced stats with tool information
                enhanced_stats = {
                    **by_severity,
                    "Total_Issues": vuln_count,
                }

                # Add tool summary if available
                if by_tool:
                    enhanced_stats["Tools_Used"] = len(by_tool)
                    for tool, count in by_tool.items():
                        tool_key = tool.capitalize().replace("_", " ")
                        enhanced_stats[f"{tool_key} Findings"] = count

                # Send advanced report with PDF URL if available
                manager.send_advanced_report(
                    target=target,
                    vuln_count=vuln_count,
                    duration=duration_str,
                    vulnerabilities=vulnerabilities_for_report if vulnerabilities_for_report else None,
                    stats=enhanced_stats,
                    report_url=pdf_path,  # Add PDF URL to Discord report
                    simple_mode=True,  # Use simple mode for better mobile compatibility
                )

            logger.info("Scan completion notification sent successfully")

        except Exception as e:
            logger.warning(f"Failed to send scan notification: {e}")
            # Don't fail the scan if notification fails

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
