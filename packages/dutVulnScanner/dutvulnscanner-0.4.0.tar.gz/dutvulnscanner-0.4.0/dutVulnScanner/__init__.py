"""DUTVulnScanner - Cross-platform vulnerability scanning tool."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("dutVulnScanner")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development environment
    __version__ = "0.3.0"

__author__ = "Phan Văn Tài, Trần Đình Mạnh, Mai Xuân Trường"
__description__ = "A comprehensive vulnerability scanning framework"
__authors__ = [
    {"name": "Phan Văn Tài", "email": "taiphanvan2403@gmail.com"},
    {"name": "Trần Đình Mạnh", "email": "trandinhmanh301103@gmail.com"},
    {"name": "Mai Xuân Trường", "email": "mxtruongqb656@gmail.com"},
]
