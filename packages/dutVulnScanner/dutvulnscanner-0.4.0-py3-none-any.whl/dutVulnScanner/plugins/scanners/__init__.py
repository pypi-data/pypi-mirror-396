"""Scanner plugins for vulnerability detection."""

from .nuclei import NucleiAdapter
from .sslscan import SslscanAdapter
from .testssl import TestSSLAdapter
from .nikto import NiktoAdapter

__all__ = ["NucleiAdapter", "SslscanAdapter", "TestSSLAdapter", "NiktoAdapter"]
