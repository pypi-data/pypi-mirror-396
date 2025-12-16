"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path


@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing."""
    return {
        "runners": {
            "local": {"enabled": True, "timeout": 3600},
            "ssh": {"enabled": True, "default_port": 22},
            "docker": {"enabled": True, "default_image": "dutVulnScanner:latest"},
        },
        "adapters": {
            "nmap": {"enabled": True, "path": "nmap"},
            "nuclei": {"enabled": True, "path": "nuclei"},
            "whatweb": {"enabled": True, "path": "whatweb"},
        },
        "correlation": {
            "enabled": True,
            "confidence_threshold": 0.7,
        },
    }


@pytest.fixture
def sample_vulnerability():
    """Provide a sample vulnerability for testing."""
    return {
        "id": "test-vuln-1",
        "title": "Test Vulnerability",
        "description": "This is a test vulnerability",
        "severity": "high",
        "host": "example.com",
        "port": 80,
        "service": "http",
        "detected_by": "nmap",
        "detection_time": "2024-01-01T00:00:00",
        "cve_ids": ["CVE-2024-1234"],
        "cwe_ids": ["CWE-79"],
    }


@pytest.fixture
def sample_scan_results():
    """Provide sample scan results for testing."""
    return {
        "scan_id": "test-scan-123",
        "target": "example.com",
        "profile": "web",
        "start_time": "2024-01-01T00:00:00",
        "end_time": "2024-01-01T00:10:00",
        "duration": 600.0,
        "vulnerabilities": [
            {
                "id": "vuln-1",
                "title": "SQL Injection",
                "severity": "critical",
                "host": "example.com",
                "detected_by": "nuclei",
            }
        ],
        "tools_used": ["nmap", "nuclei", "whatweb"],
        "runner_type": "local",
        "status": "completed",
        "statistics": {
            "total": 1,
            "by_severity": {
                "critical": 1,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
        },
    }
