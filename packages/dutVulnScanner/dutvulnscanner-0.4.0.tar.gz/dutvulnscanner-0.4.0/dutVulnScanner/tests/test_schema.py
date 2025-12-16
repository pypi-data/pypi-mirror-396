"""Test schema validation."""
import pytest
from dutVulnScanner.core.schema import (
    Vulnerability,
    ScanResult,
    ScanProfile,
    SeverityLevel,
    validate_profile,
    create_vulnerability_dict,
)


class TestSchema:
    """Test schema definitions and validation."""
    
    def test_vulnerability_creation(self):
        """Test creating a vulnerability."""
        vuln = Vulnerability(
            id="test-1",
            title="Test Vulnerability",
            description="Test description",
            severity=SeverityLevel.HIGH,
            host="example.com",
            detected_by="nmap",
            detection_time="2024-01-01T00:00:00",
        )
        
        assert vuln.id == "test-1"
        assert vuln.severity == SeverityLevel.HIGH
    
    def test_vulnerability_with_cvss(self):
        """Test vulnerability with CVSS score."""
        vuln = Vulnerability(
            id="test-2",
            title="Test",
            description="Test",
            severity=SeverityLevel.CRITICAL,
            cvss_score=9.8,
            host="example.com",
            detected_by="nuclei",
            detection_time="2024-01-01T00:00:00",
        )
        
        assert vuln.cvss_score == 9.8
    
    def test_invalid_cvss_score(self):
        """Test that invalid CVSS scores are rejected."""
        with pytest.raises(Exception):
            Vulnerability(
                id="test-3",
                title="Test",
                description="Test",
                severity=SeverityLevel.HIGH,
                cvss_score=11.0,  # Invalid: > 10
                host="example.com",
                detected_by="test",
                detection_time="2024-01-01T00:00:00",
            )
    
    def test_scan_profile_validation(self):
        """Test scan profile validation."""
        profile = ScanProfile(
            name="test",
            description="Test profile",
            tools=["nmap", "nuclei"],
        )
        
        assert profile.name == "test"
        assert len(profile.tools) == 2
    
    def test_profile_requires_tools(self):
        """Test that profile requires at least one tool."""
        with pytest.raises(Exception):
            ScanProfile(
                name="test",
                description="Test",
                tools=[],  # Empty tools list
            )
    
    def test_create_vulnerability_dict(self):
        """Test helper function for creating vulnerability dict."""
        vuln = create_vulnerability_dict(
            title="Test Vuln",
            description="Test description",
            severity="high",
            host="example.com",
            detected_by="nmap",
        )
        
        assert vuln["title"] == "Test Vuln"
        assert vuln["severity"] == "high"
        assert "id" in vuln
        assert "detection_time" in vuln
    
    def test_validate_web_profile(self):
        """Test validation of web profile."""
        is_valid, errors = validate_profile("web")
        
        assert is_valid
        assert len(errors) == 0
