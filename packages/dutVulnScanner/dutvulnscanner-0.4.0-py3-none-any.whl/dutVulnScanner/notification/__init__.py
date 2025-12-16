"""
Notification module for DUTVulnScanner
Provides toast notifications and Discord webhooks
"""

from .base import Notification, NotificationType
from .toast import ToastNotification
from .discord import DiscordNotification
from .manager import NotificationManager

__all__ = ["Notification", "NotificationType", "ToastNotification", "DiscordNotification", "NotificationManager"]
