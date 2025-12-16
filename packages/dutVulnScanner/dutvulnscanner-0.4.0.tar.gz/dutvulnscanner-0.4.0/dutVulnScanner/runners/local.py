"""Local runner - executes scans on the local machine."""
import subprocess
import logging
from typing import Dict, Any

from .base import BaseRunner


logger = logging.getLogger(__name__)


class LocalRunner(BaseRunner):
    """
    Executes scanning tools locally on the current machine.
    
    This is the default and simplest runner.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize local runner."""
        super().__init__(config)
        self.timeout = config.get("runners", {}).get("local", {}).get("timeout", 3600)
    
    def execute(self, adapter, target: str, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an adapter locally.
        
        Args:
            adapter: Adapter instance with run() method
            target: Target to scan
            tool_config: Tool-specific configuration
            
        Returns:
            Scan results from the adapter
        """
        logger.info(f"Executing {adapter.name} locally against {target}")
        
        try:
            # Execute the adapter
            results = adapter.run(target, tool_config)
            
            logger.info(f"{adapter.name} execution completed")
            return results
            
        except subprocess.TimeoutExpired:
            logger.error(f"{adapter.name} execution timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"{adapter.name} execution failed: {str(e)}")
            raise
    
    def check_availability(self) -> bool:
        """Local runner is always available."""
        return True
    
    def verify_tool(self, tool_path: str) -> bool:
        """
        Verify that a tool is installed and accessible.
        
        Args:
            tool_path: Path or command name of the tool
            
        Returns:
            True if tool is available, False otherwise
        """
        try:
            result = subprocess.run(
                [tool_path, "--version"],
                capture_output=True,
                timeout=5,
                text=True,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
