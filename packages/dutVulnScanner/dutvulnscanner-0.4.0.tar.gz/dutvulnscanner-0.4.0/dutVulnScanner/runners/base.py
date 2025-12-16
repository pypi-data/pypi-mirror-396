"""Base runner interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseRunner(ABC):
    """Base class for all runners."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize runner with configuration."""
        self.config = config
    
    @abstractmethod
    def execute(self, adapter, target: str, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an adapter against a target.
        
        Args:
            adapter: Adapter instance to execute
            target: Target host/IP
            tool_config: Tool-specific configuration
            
        Returns:
            Execution results dictionary
        """
        pass
    
    @abstractmethod
    def check_availability(self) -> bool:
        """Check if this runner is available in the current environment."""
        pass
