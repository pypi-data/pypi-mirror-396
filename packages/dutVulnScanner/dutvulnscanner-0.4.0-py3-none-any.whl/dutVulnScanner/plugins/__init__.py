"""Plugins for various security scanning tools."""

from .base import BaseAdapter

from .recon import WhoisAdapter, NmapAdapter, WhatWebAdapter, SubfinderAdapter, NaabuAdapter, HttpxAdapter
from .scanners import NucleiAdapter, SslscanAdapter, TestSSLAdapter, NiktoAdapter
from .validators import SqlmapAdapter, HydraAdapter, DalfoxAdapter


AVAILABLE_ADAPTERS = {
    # Reconnaissance tools
    "whois": WhoisAdapter,
    "nmap": NmapAdapter,
    "whatweb": WhatWebAdapter,
    "subfinder": SubfinderAdapter,
    "naabu": NaabuAdapter,
    "httpx": HttpxAdapter,
    # Vulnerability scanners
    "nuclei": NucleiAdapter,
    "sslscan": SslscanAdapter,
    "testssl": TestSSLAdapter,
    "nikto": NiktoAdapter,
    # Validators/Exploitation tools
    "sqlmap": SqlmapAdapter,
    "hydra": HydraAdapter,
    "dalfox": DalfoxAdapter,
}

# Categorized adapters
ADAPTERS_BY_CATEGORY = {
    "recon": {
        "whois": WhoisAdapter,
        "nmap": NmapAdapter,
        "whatweb": WhatWebAdapter,
        "subfinder": SubfinderAdapter,
        "naabu": NaabuAdapter,
        "httpx": HttpxAdapter,
    },
    "scanners": {
        "nuclei": NucleiAdapter,
        "sslscan": SslscanAdapter,
        "testssl": TestSSLAdapter,
        "nikto": NiktoAdapter,
    },
    "validators": {
        "sqlmap": SqlmapAdapter,
        "hydra": HydraAdapter,
        "dalfox": DalfoxAdapter,
    },
}


def get_adapter(name: str, config: dict):
    """
    Get an adapter instance by name.

    Args:
        name: Adapter name
        config: Configuration dictionary

    Returns:
        Adapter instance

    Raises:
        ValueError: If adapter not found
    """
    if name not in AVAILABLE_ADAPTERS:
        raise ValueError(f"Unknown adapter: {name}")

    adapter_class = AVAILABLE_ADAPTERS[name]
    return adapter_class(config)


__all__ = [
    "BaseAdapter",
    # Recon
    "WhoisAdapter",
    "NmapAdapter",
    "WhatWebAdapter",
    "SubfinderAdapter",
    "NaabuAdapter",
    "HttpxAdapter",
    # Scanners
    "NucleiAdapter",
    "SslscanAdapter",
    "TestSSLAdapter",
    "NiktoAdapter",
    # Validators
    "SqlmapAdapter",
    "HydraAdapter",
    "DalfoxAdapter",
    # Utils
    "AVAILABLE_ADAPTERS",
    "ADAPTERS_BY_CATEGORY",
    "get_adapter",
]
