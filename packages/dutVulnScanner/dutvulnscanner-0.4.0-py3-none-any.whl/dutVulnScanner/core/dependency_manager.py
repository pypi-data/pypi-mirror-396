"""Dependency manager - check and install security tools."""

import subprocess
import shutil
import logging
import os
import platform
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from enum import Enum

from rich.console import Console

from .tool_registry import (
    get_tool_info,
    get_all_tools,
    get_install_command,
    InstallMethod,
    ToolCategory,
)

logger = logging.getLogger(__name__)


class ToolStatus(str, Enum):
    """Tool availability status."""
    INSTALLED = "installed"
    NOT_FOUND = "not_found"
    ERROR = "error"


class DependencyManager:
    """
    Manages security tool dependencies.
    
    Responsibilities:
    - Check if tools are installed
    - Get tool versions
    - Install missing tools
    - Verify installations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize dependency manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.install_dir = Path.home() / ".dutvulnscanner" / "bin"
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Rich console for pretty output
        self.console = Console()
        
        # Add custom bin to PATH for this session
        if str(self.install_dir) not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{self.install_dir}:{os.environ.get('PATH', '')}"
    
    def check_tool(self, tool_name: str) -> Dict[str, Any]:
        """
        Check if a tool is installed and get its version.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            Dictionary with:
                - status: ToolStatus
                - version: Version string (if found)
                - path: Path to executable (if found)
                - error: Error message (if error)
        """
        tool_info = get_tool_info(tool_name)
        if not tool_info:
            return {
                "status": ToolStatus.ERROR,
                "error": f"Tool '{tool_name}' not in registry",
            }
        
        # Check if tool exists in PATH
        tool_path = shutil.which(tool_name)
        
        # If not found in PATH, check GOBIN for Go tools
        if not tool_path and tool_info.get("install_methods", {}).get("linux", {}).get("primary") == InstallMethod.GO:
            gopath = os.environ.get("GOPATH", str(Path.home() / "go"))
            gobin = os.environ.get("GOBIN", f"{gopath}/bin")
            potential_path = Path(gobin) / tool_name
            if potential_path.exists() and potential_path.is_file():
                tool_path = str(potential_path)
                # Add to PATH for current session
                if gobin not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = f"{gobin}:{os.environ.get('PATH', '')}"
        
        if not tool_path:
            return {
                "status": ToolStatus.NOT_FOUND,
                "version": None,
                "path": None,
            }
        
        # Try to get version
        version = self._get_tool_version(tool_name, tool_info)
        
        return {
            "status": ToolStatus.INSTALLED,
            "version": version,
            "path": tool_path,
        }
    
    def _get_tool_version(self, tool_name: str, tool_info: Dict[str, Any]) -> Optional[str]:
        """Get tool version by running check command."""
        check_cmd = tool_info.get("check_command")
        if not check_cmd:
            return None
        
        try:
            result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            # Parse version from output
            output = result.stdout + result.stderr
            version = self._parse_version(output)
            return version
            
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"Failed to get version for {tool_name}: {e}")
            return None
    
    def _parse_version(self, output: str) -> Optional[str]:
        """Parse version string from command output."""
        import re
        
        # Common version patterns
        patterns = [
            r'v?(\d+\.\d+\.\d+)',  # v1.2.3 or 1.2.3
            r'version[:\s]+v?(\d+\.\d+\.\d+)',  # version: 1.2.3
            r'(\d+\.\d+)',  # 1.2
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def check_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Check status of all registered tools.
        
        Returns:
            Dictionary mapping tool names to their status info
        """
        results = {}
        for tool_name in get_all_tools():
            results[tool_name] = self.check_tool(tool_name)
        return results
    
    def check_profile_tools(self, profile_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Check tools required for a specific profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Dictionary mapping tool names to their status info
        """
        from .tool_registry import get_tools_by_profile
        
        tools = get_tools_by_profile(profile_name)
        results = {}
        for tool_name in tools:
            results[tool_name] = self.check_tool(tool_name)
        return results
    
    def get_missing_tools(self, tools: Optional[List[str]] = None) -> List[str]:
        """
        Get list of missing tools.
        
        Args:
            tools: List of tool names to check (None = check all)
            
        Returns:
            List of missing tool names
        """
        if tools is None:
            tools = get_all_tools()
        
        missing = []
        for tool in tools:
            status = self.check_tool(tool)
            if status["status"] == ToolStatus.NOT_FOUND:
                missing.append(tool)
        
        return missing
    
    def check_go_installed(self) -> bool:
        """Check if Go compiler is installed."""
        return shutil.which("go") is not None
    
    def _calculate_install_steps(self, method: InstallMethod, tool_info: Dict[str, Any]) -> int:
        """Calculate total steps needed for installation."""
        has_post_install = bool(tool_info.get("post_install"))
        
        if method == InstallMethod.APT:
            # APT: 1) update, 2) install, 3) post-install (if any)
            return 3 if has_post_install else 2
        elif method == InstallMethod.GO:
            # GO: Check if Go compiler needed
            needs_go = not self.check_go_installed()
            if needs_go:
                # 1) Install Go, 2) Verify Go, 3) go install, 4) post-install (if any)
                return 4 if has_post_install else 3
            else:
                # 1) go install, 2) post-install (if any)
                return 2 if has_post_install else 1
        elif method == InstallMethod.BINARY:
            # BINARY: 1) download/install, 2) post-install (if any)
            return 2 if has_post_install else 1
        else:
            return 1
    
    def install_tool(
        self,
        tool_name: str,
        method: Optional[InstallMethod] = None,
        sudo_password: Optional[str] = None,
        progress_callback: Optional[callable] = None,
    ) -> Tuple[bool, str]:
        """
        Install a tool.
        
        Args:
            tool_name: Name of tool to install
            method: Installation method (if None, use primary)
            sudo_password: Sudo password for apt installs
            progress_callback: Optional callback(action, value) to control progress display
                              action: 'update' | 'pause' | 'resume' | 'step'
                              value: message string for update, True/False for pause/resume, or step number
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        tool_info = get_tool_info(tool_name)
        if not tool_info:
            return False, f"Tool '{tool_name}' not in registry"
        
        # Get installation method
        os_name = platform.system().lower()
        install_info = tool_info["install_methods"].get(os_name)
        if not install_info:
            return False, f"Installation not supported on {os_name}"
        
        install_method = method or install_info.get("primary")
        
        # Calculate total steps for this installation
        total_steps = self._calculate_install_steps(install_method, tool_info)
        
        # Notify total steps to progress
        if progress_callback:
            progress_callback('init', total_steps)
        
        # Install based on method
        if install_method == InstallMethod.APT:
            success, msg = self._install_via_apt(tool_name, install_info, sudo_password, progress_callback, tool_info)
        elif install_method == InstallMethod.GO:
            success, msg = self._install_via_go(tool_name, install_info, progress_callback, tool_info)
        elif install_method == InstallMethod.BINARY:
            success, msg = self._install_via_binary(tool_name, install_info, progress_callback, tool_info)
        else:
            return False, f"Installation method '{install_method}' not implemented"
        
        if not success:
            return False, msg
        
        # Run post-install command if specified
        post_install = tool_info.get("post_install")
        if post_install:
            # Update progress to post-install step
            if progress_callback:
                # Calculate which step this is
                if install_method == InstallMethod.GO:
                    go_was_missing = 'go_was_missing' in locals() and go_was_missing
                    post_step = 4 if go_was_missing else 2
                elif install_method == InstallMethod.APT:
                    post_step = 3
                else:
                    post_step = 2
                
                total_steps = self._calculate_install_steps(install_method, tool_info)
                progress_callback('step', post_step)
                progress_callback('update', f"[{post_step}/{total_steps}] Running post-install...")
            
            logger.info(f"Running post-install: {post_install}")
            self.console.print(f"  [yellow]⚙️  Running post-install commands...[/yellow]")
            try:
                result = subprocess.run(post_install, shell=True, check=False, timeout=120, capture_output=True, text=True)
                if result.returncode == 0:
                    self.console.print(f"  [green]✓[/green] Post-install completed")
                else:
                    logger.warning(f"Post-install returned non-zero: {result.stderr}")
            except Exception as e:
                logger.warning(f"Post-install failed: {e}")
        
        # Verify installation
        status = self.check_tool(tool_name)
        if status["status"] == ToolStatus.INSTALLED:
            return True, f"Successfully installed {tool_name}"
        else:
            return False, f"Installation completed but tool not found in PATH"
    
    def _install_via_apt(
        self,
        tool_name: str,
        install_info: Dict[str, Any],
        sudo_password: Optional[str] = None,
        progress_callback: Optional[callable] = None,
        tool_info: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """Install tool via apt package manager."""
        package = install_info.get("apt_package")
        if not package:
            return False, "APT package not available"
        
        # Check if sudo is available
        try:
            subprocess.run(["which", "sudo"], capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "sudo not found. Please install sudo first."
        
        try:
            # Step 1: Updating apt
            if progress_callback:
                progress_callback('step', 1)
                progress_callback('update', f"[1/3] 📦 Processing updating apt repositories...")
            
            logger.info("Updating apt package list...")
            
            # Pause progress before sudo (may need password)
            if progress_callback:
                progress_callback('pause', True)
            
            subprocess.run(
                ["sudo", "apt-get", "update", "-qq"],
                check=True,
                capture_output=True,
                timeout=60,
            )
            
            # Resume progress
            if progress_callback:
                progress_callback('resume', False)
            
            time.sleep(0.5)  # Delay to show completion
            
            # Step 2: Installing package
            if progress_callback:
                progress_callback('step', 2)
                progress_callback('update', f"[2/3] ⚙️  Processing installing {package}...")
            
            logger.info(f"Installing {package} via apt...")
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", package],
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            if result.returncode != 0:
                if progress_callback:
                    progress_callback('resume', False)
                return False, f"apt install failed: {result.stderr}"
            
            time.sleep(0.5)  # Delay to show completion
            
            # Step 3: Verifying installation
            if progress_callback:
                progress_callback('step', 3)
                progress_callback('update', f"[3/3] ✓ Processing verifying {tool_name}...")
            
            self.console.print(f"  [green]✓[/green] {package} installed successfully")
            return True, f"Installed {package} via apt"
            
        except subprocess.TimeoutExpired:
            if progress_callback:
                progress_callback('resume', False)
            return False, "Installation timed out"
        except subprocess.CalledProcessError as e:
            return False, f"Installation failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def _install_via_go(
        self,
        tool_name: str,
        install_info: Dict[str, Any],
        progress_callback: Optional[callable] = None,
        tool_info: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """Install tool via go install."""
        # Check if Go is installed at the beginning
        go_was_missing = not self.check_go_installed()
        
        current_step = 1
        total_steps = 4 if go_was_missing else 2
        
        # If Go is missing, install it first
        if go_was_missing:
            logger.info("Go compiler not found. Installing golang-go...")
            
            if progress_callback:
                progress_callback('step', current_step)
                progress_callback('update', f"[{current_step}/{total_steps}] 🔧 Processing installing Go compiler...")
            
            self.console.print("  [yellow]⚙️  Installing Go compiler first...[/yellow]")
            
            # Pause for sudo
            if progress_callback:
                progress_callback('pause', True)
            
            try:
                # Install Go via apt
                result = subprocess.run(
                    ["sudo", "apt-get", "install", "-y", "golang-go"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                
                if result.returncode != 0:
                    if progress_callback:
                        progress_callback('resume', False)
                    return False, f"Failed to install Go compiler: {result.stderr}"
                
                # Resume progress
                if progress_callback:
                    progress_callback('resume', False)
                
                time.sleep(0.5)  # Delay to show completion
                
                if progress_callback:
                    current_step += 1
                    progress_callback('step', current_step)
                    progress_callback('update', f"[{current_step}/{total_steps}] 📦 Processing preparing {tool_name}...")
                
                self.console.print("  [green]✓[/green] Go compiler installed successfully")
                
                # Verify Go is now available
                if not self.check_go_installed():
                    return False, "Go installed but not found in PATH. Try: export PATH=$PATH:/usr/lib/go-1.19/bin"
                    
            except subprocess.TimeoutExpired:
                if progress_callback:
                    progress_callback('resume', False)
                return False, "Go installation timed out"
            except Exception as e:
                if progress_callback:
                    progress_callback('resume', False)
                return False, f"Failed to install Go: {e}"
        
        go_package = install_info.get("go_package")
        if not go_package:
            return False, "Go package not available"
        
        try:
            logger.info(f"Installing {tool_name} via go install...")
            
            current_step += 1
            if progress_callback:
                progress_callback('step', current_step)
                progress_callback('update', f"[{current_step}/{total_steps}] 📦 Processing downloading {tool_name}...")
            
            # Set GOPATH if not set
            gopath = os.environ.get("GOPATH", str(Path.home() / "go"))
            gobin = os.environ.get("GOBIN", f"{gopath}/bin")
            
            env = os.environ.copy()
            env["GOPATH"] = gopath
            env["GOBIN"] = gobin
            
            result = subprocess.run(
                ["go", "install", "-v", go_package],
                capture_output=True,
                text=True,
                timeout=300,
                env=env,
            )
            
            if result.returncode != 0:
                return False, f"go install failed: {result.stderr}"
            
            # Add GOBIN to PATH if not already there
            if gobin not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{gobin}:{os.environ.get('PATH', '')}"
            
            time.sleep(0.5)  # Delay to show completion
            
            current_step += 1
            if progress_callback:
                progress_callback('step', current_step)
                progress_callback('update', f"[{current_step}/{total_steps}] ✓ Processing verifying {tool_name}...")
                
                # Also add to shell profile for persistence
                try:
                    shell_rc = Path.home() / ".bashrc"
                    if shell_rc.exists():
                        with open(shell_rc, "r") as f:
                            content = f.read()
                        
                        # Check if GOBIN already in PATH
                        if f'export PATH="$PATH:{gobin}"' not in content and f'export PATH=$PATH:{gobin}' not in content:
                            with open(shell_rc, "a") as f:
                                f.write(f'\n# Added by DUTVulnScanner\nexport PATH="$PATH:{gobin}"\n')
                            logger.info(f"Added {gobin} to .bashrc")
                except Exception as e:
                    logger.warning(f"Failed to update .bashrc: {e}")
            
            self.console.print(f"  [green]✓[/green] {tool_name} installed successfully")
            return True, f"Installed {tool_name} via go install"
            
        except subprocess.TimeoutExpired:
            return False, "Installation timed out"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def _install_via_binary(
        self,
        tool_name: str,
        install_info: Dict[str, Any],
        progress_callback: Optional[callable] = None,
        tool_info: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """Install tool by downloading binary."""
        binary_url = install_info.get("binary_url")
        apt_package = install_info.get("apt_package")
        
        # For testssl.sh, try apt first if available (easier than downloading)
        if apt_package and tool_name == "testssl":
            try:
                if progress_callback:
                    progress_callback('update', f"⚙️  Installing {tool_name} via apt...")
                
                logger.info(f"Installing {tool_name} via apt...")
                
                # Pause for sudo
                if progress_callback:
                    progress_callback('pause', True)
                
                # Update package list
                subprocess.run(
                    ["sudo", "apt-get", "update", "-qq"],
                    capture_output=True,
                    timeout=120,
                )
                
                # Install via apt
                result = subprocess.run(
                    ["sudo", "apt-get", "install", "-y", apt_package],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                
                if result.returncode == 0:
                    if progress_callback:
                        progress_callback('resume', False)
                    self.console.print(f"  [green]✓[/green] {apt_package} installed successfully")
                    return True, f"Installed {apt_package} via apt"
                
                # Failed, resume progress
                if progress_callback:
                    progress_callback('resume', False)
                    
            except Exception as e:
                if progress_callback:
                    progress_callback('resume', False)
                logger.warning(f"apt install failed, will try binary: {e}")
        
        # Fallback to binary download
        if not binary_url:
            return False, "Binary URL not available and apt install failed"
        
        return False, f"Please manually download and install from: {binary_url}"
    
    def get_install_instructions(self, tool_name: str) -> str:
        """
        Get human-readable installation instructions.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Installation instructions as string
        """
        tool_info = get_tool_info(tool_name)
        if not tool_info:
            return f"Tool '{tool_name}' not found in registry"
        
        instructions = []
        instructions.append(f"📦 {tool_name}")
        instructions.append(f"   {tool_info['description']}")
        instructions.append(f"   🏠 Homepage: {tool_info['homepage']}")
        instructions.append("")
        instructions.append("   📥 Installation methods:")
        
        os_name = platform.system().lower()
        install_info = tool_info["install_methods"].get(os_name, {})
        
        if install_info.get("apt_package"):
            instructions.append(f"   • APT: sudo apt-get install -y {install_info['apt_package']}")
        
        if install_info.get("go_package"):
            instructions.append(f"   • Go: go install -v {install_info['go_package']}")
        
        if install_info.get("binary_url"):
            instructions.append(f"   • Binary: {install_info['binary_url']}")
        
        if tool_info.get("warning"):
            instructions.append("")
            instructions.append(f"   {tool_info['warning']}")
        
        return "\n".join(instructions)
