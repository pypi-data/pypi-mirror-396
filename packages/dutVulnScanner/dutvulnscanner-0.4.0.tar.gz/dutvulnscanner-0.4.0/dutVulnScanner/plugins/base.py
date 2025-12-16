"""Base adapter interface for security scanning tools."""

from abc import ABC, abstractmethod  # ABC: Abstract Base Class
from typing import Dict, Any, Optional


class BaseAdapter(ABC):
    """
    Base class for all scanning tool adapters. ABC: Abstract Base Class

    Each adapter wraps a specific security tool (nmap, nuclei, etc.)
    and provides a standardized interface for execution and result parsing.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize adapter.

        Args:
            config: Global configuration dictionary
        """
        self.config = config
        # Use _tool_name to avoid conflict with @property name in subclasses
        self._tool_name = self.__class__.__name__.replace("Adapter", "").lower()
        self.tool_config = config.get("adapters", {}).get(self._tool_name, {})

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of the tool."""
        pass

    @abstractmethod
    def build_command(self, target: str, options: Dict[str, Any]) -> str:
        """
        Build the command to execute the tool.

        Args:
            target: Target host/IP to scan
            options: Tool-specific options

        Returns:
            Command string to execute
        """
        pass

    @abstractmethod
    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse tool output into standardized format.

        Args:
            output: Raw tool output

        Returns:
            Dictionary with vulnerabilities and metadata
        """
        pass

    def run(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool and return parsed results.

        Args:
            target: Target to scan
            options: Tool-specific options

        Returns:
            Scan results dictionary
        """
        import subprocess

        command = self.build_command(target, options)
        
        # Get timeout: prioritize tool_config, then options, then default 600s (10 minutes)
        timeout = self.tool_config.get("timeout", options.get("timeout", 600))

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0 and not self.allows_non_zero_exit():
            raise RuntimeError(f"{self._tool_name} failed with exit code {result.returncode}: {result.stderr}")

        return self.parse_output(result.stdout)

    def allows_non_zero_exit(self) -> bool:
        """
        Check if the tool can exit with non-zero code on success.

        Some tools return non-zero when they find vulnerabilities.

        Returns:
            True if non-zero exit codes are acceptable
        """
        return False

    def get_docker_image(self) -> Optional[str]:
        """
        Get the Docker image name for this tool.

        Returns:
            Docker image name or None if not available
        """
        return None

    def validate_target(self, target: str) -> bool:
        """
        Validate that the target is appropriate for this tool.

        Args:
            target: Target string

        Returns:
            True if target is valid
        """
        return bool(target and len(target) > 0)

    def get_default_options(self) -> Dict[str, Any]:
        """
        Get default options for this tool.

        Returns:
            Dictionary of default options
        """
        return {}
