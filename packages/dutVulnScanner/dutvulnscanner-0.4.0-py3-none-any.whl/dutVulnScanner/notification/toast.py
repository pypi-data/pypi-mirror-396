"""
Toast notification implementation using plyer
"""

import logging
import os
import platform
import subprocess
from typing import Optional
from .base import Notification

try:
    from plyer import notification

    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logging.warning("plyer not available, toast notifications will not work")

logger = logging.getLogger(__name__)


class ToastNotification(Notification):
    """Toast notification using plyer library"""

    def __init__(self, app_name: str = "DUTVulnScanner", timeout: int = 4):
        super().__init__(app_name)
        self.timeout = timeout
        self.icon_path = self.get_icon_path()

        # Debug: log icon path
        logger.debug(f"Toast icon path: {self.icon_path}")

        if not PLYER_AVAILABLE:
            logger.error("plyer library is required for toast notifications")
            raise ImportError("plyer library is required for toast notifications")

    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        Send toast notification

        Args:
            title: Notification title
            message: Notification message
            **kwargs: Additional arguments (icon_path, timeout)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            icon_path = kwargs.get("icon_path", self.icon_path)
            timeout = kwargs.get("timeout", self.timeout)

            # Debug: log what we're sending
            logger.debug(f"Sending notification with icon: {icon_path}")

            # Check if icon file exists
            if icon_path and os.path.exists(icon_path):
                logger.debug(f"Icon file exists: {icon_path}")
            else:
                logger.warning(f"Icon file not found: {icon_path}")
                icon_path = None  # Don't use icon if file doesn't exist

            # Try notify-send first on Linux (better icon support)
            if platform.system() == "Linux" and self._try_notify_send(title, message, icon_path, timeout):
                logger.info(f"Toast notification sent via notify-send: {title}")
                return True

            # Fallback to plyer
            notification.notify(
                title=title, message=message, app_name=self.app_name, app_icon=icon_path, timeout=timeout
            )

            logger.info(f"Toast notification sent: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send toast notification: {e}")
            return False

    def _try_notify_send(self, title: str, message: str, icon_path: Optional[str], timeout: int) -> bool:
        """
        Try to send notification using notify-send (Linux only)

        Args:
            title: Notification title
            message: Notification message
            icon_path: Path to icon file
            timeout: Timeout in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if notify-send is available
            result = subprocess.run(["which", "notify-send"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.debug("notify-send not found, using plyer instead")
                return False

            # Build notify-send command
            cmd = ["notify-send", "--app-name", self.app_name, "--expire-time", str(timeout * 1000)]

            if icon_path and os.path.exists(icon_path):
                cmd.extend(["--icon", icon_path])

            cmd.extend([title, message])

            # Execute notify-send
            subprocess.run(cmd, check=True, capture_output=True)
            logger.debug("Notification sent successfully via notify-send")
            return True

        except Exception as e:
            logger.debug(f"notify-send failed: {e}, falling back to plyer")
            return False
