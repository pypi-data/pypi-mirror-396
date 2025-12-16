"""Test adapters."""

import pytest
from dutVulnScanner.plugins import get_adapter, AVAILABLE_ADAPTERS
from dutVulnScanner.plugins.base import BaseAdapter
from dutVulnScanner.core.config import get_default_config


class TestAdapters:
    """Test scanning tool adapters."""

    def test_available_adapters(self):
        """Test that adapters are registered."""
        assert "nmap" in AVAILABLE_ADAPTERS
        assert "nuclei" in AVAILABLE_ADAPTERS
        assert "whatweb" in AVAILABLE_ADAPTERS

    def test_get_adapter(self):
        """Test getting an adapter instance."""
        config = get_default_config()

        adapter = get_adapter("nmap", config)
        assert adapter is not None
        assert adapter.name == "nmap"

    def test_get_unknown_adapter(self):
        """Test getting a non-existent adapter."""
        config = get_default_config()

        with pytest.raises(ValueError):
            get_adapter("unknown_tool", config)

    def test_nmap_adapter(self):
        """Test Nmap adapter."""
        config = get_default_config()
        adapter = get_adapter("nmap", config)

        assert adapter.description
        assert "nmap" in adapter.description.lower()

    def test_nuclei_adapter(self):
        """Test Nuclei adapter."""
        config = get_default_config()
        adapter = get_adapter("nuclei", config)

        assert adapter.description
        assert "nuclei" in adapter.description.lower()

    def test_whatweb_adapter(self):
        """Test WhatWeb adapter."""
        config = get_default_config()
        adapter = get_adapter("whatweb", config)

        assert adapter.description
        assert "web" in adapter.description.lower()

    def test_adapter_build_command(self):
        """Test building commands."""
        config = get_default_config()
        adapter = get_adapter("nmap", config)

        command = adapter.build_command("example.com", {})
        assert "nmap" in command
        assert "example.com" in command

    def test_adapter_validate_target(self):
        """Test target validation."""
        config = get_default_config()
        adapter = get_adapter("nmap", config)

        assert adapter.validate_target("example.com")
        assert adapter.validate_target("192.168.1.1")
        assert not adapter.validate_target("")
