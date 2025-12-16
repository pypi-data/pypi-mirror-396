"""
Base notification classes and enums
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
import os


class NotificationType(Enum):
    """Types of notifications supported"""

    TOAST = "toast"
    DISCORD = "discord"


class Notification(ABC):
    """Abstract base class for all notification types"""

    def __init__(self, app_name: str = "DUTVulnScanner"):
        self.app_name = app_name

    @abstractmethod
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        Send notification

        Args:
            title: Notification title
            message: Notification message
            **kwargs: Additional arguments specific to notification type

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @staticmethod
    def get_icon_path() -> str:
        """Get appropriate icon path based on OS"""
        # Check if running on Linux
        if os.name == "posix":
            return os.path.abspath("./dutVulnScanner/assets/logo.png")
        # Check if running on Windows
        elif os.name == "nt":
            return os.path.abspath("./dutVulnScanner/assets/logo.ico")
        # Check if running on macOS
        else:
            return os.path.abspath("./dutVulnScanner/assets/logo.png")
