"""
Notification manager to handle different notification types
"""

import logging
from typing import Optional, Dict, Any, List
from .base import Notification, NotificationType
from .toast import ToastNotification
from .discord import DiscordNotification

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manager class to handle multiple notification types"""

    def __init__(self):
        self.notifications: Dict[NotificationType, Notification] = {}
        self.enabled_types: List[NotificationType] = []

    def add_toast_notification(self, app_name: str = "DUTVulnScanner", timeout: int = 4) -> None:
        """Add toast notification support"""
        try:
            toast = ToastNotification(app_name, timeout)
            self.notifications[NotificationType.TOAST] = toast
            if NotificationType.TOAST not in self.enabled_types:
                self.enabled_types.append(NotificationType.TOAST)
            logger.info("Toast notification enabled")
        except ImportError as e:
            logger.warning(f"Cannot enable toast notification: {e}")

    def add_discord_notification(
        self, webhook_url: str, app_name: str = "DUTVulnScanner", username: Optional[str] = None
    ) -> None:
        """Add Discord notification support"""
        try:
            discord = DiscordNotification(webhook_url, app_name, username)
            self.notifications[NotificationType.DISCORD] = discord
            if NotificationType.DISCORD not in self.enabled_types:
                self.enabled_types.append(NotificationType.DISCORD)
            logger.info("Discord notification enabled")
        except (ImportError, ValueError) as e:
            logger.warning(f"Cannot enable Discord notification: {e}")

    def remove_notification(self, notification_type: NotificationType) -> None:
        """Remove a notification type"""
        if notification_type in self.notifications:
            del self.notifications[notification_type]
            if notification_type in self.enabled_types:
                self.enabled_types.remove(notification_type)
            logger.info(f"Removed {notification_type.value} notification")

    def send_notification(
        self, title: str, message: str, notification_types: Optional[List[NotificationType]] = None, **kwargs
    ) -> Dict[NotificationType, bool]:
        """
        Send notification to specified types or all enabled types

        Args:
            title: Notification title
            message: Notification message
            notification_types: List of notification types to send to (default: all enabled)
            **kwargs: Additional arguments for specific notification types

        Returns:
            Dict mapping notification types to success status
        """
        if notification_types is None:
            notification_types = self.enabled_types

        results = {}

        for notification_type in notification_types:
            if notification_type in self.notifications:
                try:
                    success = self.notifications[notification_type].send(title, message, **kwargs)
                    results[notification_type] = success
                except Exception as e:
                    logger.error(f"Failed to send {notification_type.value} notification: {e}")
                    results[notification_type] = False
            else:
                logger.warning(f"Notification type {notification_type.value} not configured")
                results[notification_type] = False

        return results

    def send_toast(self, title: str, message: str, **kwargs) -> bool:
        """Send toast notification"""
        return self.send_notification(title, message, [NotificationType.TOAST], **kwargs).get(
            NotificationType.TOAST, False
        )

    def send_discord(self, title: str, message: str, **kwargs) -> bool:
        """Send Discord notification"""
        return self.send_notification(title, message, [NotificationType.DISCORD], **kwargs).get(
            NotificationType.DISCORD, False
        )

    def send_discord_simple(self, message: str) -> bool:
        """Send simple Discord message"""
        if NotificationType.DISCORD in self.notifications:
            discord_notif: DiscordNotification = self.notifications[NotificationType.DISCORD]
            return discord_notif.send_simple(message)
        else:
            logger.warning("Discord notification not configured")
            return False

    def send_advanced_report(self, target: str, vuln_count: int, duration: str, **kwargs) -> bool:
        """
        Send advanced, visually stunning scan report via Discord (if enabled)

        Args:
            target: Target that was scanned
            vuln_count: Number of vulnerabilities found
            duration: Scan duration
            **kwargs: Additional arguments (vulnerabilities, stats, report_url, mention, simple_mode, etc.)

        Returns:
            bool: True if Discord is enabled and sent successfully, False otherwise
        """
        if NotificationType.DISCORD in self.notifications:
            discord_notif: DiscordNotification = self.notifications[NotificationType.DISCORD]
            return discord_notif.send_advanced_report(target, vuln_count, duration, **kwargs)
        else:
            logger.warning("Discord notification not configured for advanced reports")
            return False

    def send_responsive_report(self, target: str, vuln_count: int, duration: str, **kwargs) -> bool:
        """
        Send scan report with automatic responsive mode selection

        Args:
            target: Target that was scanned
            vuln_count: Number of vulnerabilities found
            duration: Scan duration
            **kwargs: Additional arguments (auto_mobile=True for auto-detection)

        Returns:
            bool: True if Discord is enabled and sent successfully, False otherwise
        """
        # Auto-detect mobile mode based on context or explicit setting
        auto_mobile = kwargs.pop("auto_mobile", False)

        if auto_mobile:
            # Simple heuristics to detect if mobile/tablet view might be better
            # This could be enhanced with actual device detection if webhook supports it
            simple_mode = True
            kwargs["simple_mode"] = simple_mode

        return self.send_advanced_report(target, vuln_count, duration, **kwargs)

    def send_pdf_report_notification(self, target: str, pdf_path: str, creation_time: str = None, **kwargs) -> bool:
        """
        Send notification about PDF report generation completion.

        Args:
            target: Target host/IP scanned
            pdf_path: Path to generated PDF file
            creation_time: When the PDF was created (ISO format)
            **kwargs: Additional parameters for Discord embed

        Returns:
            True if notification sent successfully
        """
        # First send toast notification
        if NotificationType.TOAST in self.notifications:
            try:
                toast = self.notifications[NotificationType.TOAST]
                toast.notify(title="📄 PDF Report Generated", message=f"PDF report ready for {target}")
            except Exception as e:
                logger.warning(f"Failed to send toast for PDF report: {e}")

        # Then send Discord notification if available
        if NotificationType.DISCORD in self.notifications:
            try:
                discord_notif = self.notifications[NotificationType.DISCORD]
                return discord_notif.send_pdf_report_notification(target, pdf_path, creation_time, **kwargs)
            except Exception as e:
                logger.error(f"Failed to send Discord PDF notification: {e}")
                return False

        return True

    def get_enabled_types(self) -> List[NotificationType]:
        """Get list of enabled notification types"""
        return self.enabled_types.copy()

    def is_enabled(self, notification_type: NotificationType) -> bool:
        """Check if a notification type is enabled"""
        return notification_type in self.enabled_types


def create_notification_manager(
    discord_webhook: Optional[str] = None, enable_toast: bool = True, app_name: str = "DUTVulnScanner"
) -> NotificationManager:
    """
    Factory function to create notification manager with common configuration

    Args:
        discord_webhook: Discord webhook URL (optional)
        enable_toast: Whether to enable toast notifications
        app_name: Application name

    Returns:
        Configured NotificationManager
    """
    manager = NotificationManager()

    if enable_toast:
        manager.add_toast_notification(app_name)

    if discord_webhook:
        manager.add_discord_notification(discord_webhook, app_name)

    return manager
