"""Test correlation engine."""
import pytest
from dutVulnScanner.core.correlation import CorrelationEngine
from dutVulnScanner.core.config import get_default_config
from dutVulnScanner.core.schema import create_vulnerability_dict


class TestCorrelation:
    """Test vulnerability correlation."""
    
    def test_correlation_engine_init(self):
        """Test initializing correlation engine."""
        config = get_default_config()
        engine = CorrelationEngine(config)
        
        assert engine is not None
        assert engine.enabled
    
    def test_correlate_empty_list(self):
        """Test correlating empty vulnerability list."""
        config = get_default_config()
        engine = CorrelationEngine(config)
        
        result = engine.correlate([])
        assert result == []
    
    def test_correlate_single_vulnerability(self):
        """Test correlating a single vulnerability."""
        config = get_default_config()
        engine = CorrelationEngine(config)
        
        vuln = create_vulnerability_dict(
            title="Test Vuln",
            description="Test",
            severity="high",
            host="example.com",
            detected_by="nmap",
        )
        
        result = engine.correlate([vuln])
        assert len(result) == 1
    
    def test_correlate_duplicate_vulnerabilities(self):
        """Test correlating duplicate vulnerabilities."""
        config = get_default_config()
        engine = CorrelationEngine(config)
        
        vuln1 = create_vulnerability_dict(
            title="SQL Injection vulnerability",
            description="SQL injection found",
            severity="high",
            host="example.com",
            port=80,
            detected_by="nmap",
            cve_ids=["CVE-2024-1234"],
        )
        
        vuln2 = create_vulnerability_dict(
            title="SQL Injection vulnerability",
            description="SQL injection detected",
            severity="critical",
            host="example.com",
            port=80,
            detected_by="nuclei",
            cve_ids=["CVE-2024-1234"],
        )
        
        result = engine.correlate([vuln1, vuln2])
        
        # Should merge into one vulnerability
        assert len(result) == 1
        assert result[0]["correlated"] == True
        assert result[0]["source_count"] == 2
        assert "nmap" in result[0]["detected_by"]
        assert "nuclei" in result[0]["detected_by"]
    
    def test_correlate_different_vulnerabilities(self):
        """Test correlating different vulnerabilities."""
        config = get_default_config()
        engine = CorrelationEngine(config)
        
        vuln1 = create_vulnerability_dict(
            title="XSS vulnerability",
            description="Cross-site scripting found",
            severity="medium",
            host="example.com",
            detected_by="nuclei",
        )
        
        vuln2 = create_vulnerability_dict(
            title="SQL Injection",
            description="SQL injection found",
            severity="high",
            host="example.com",
            detected_by="nmap",
        )
        
        result = engine.correlate([vuln1, vuln2])
        
        # Should keep both vulnerabilities
        assert len(result) == 2
    
    def test_severity_merging(self):
        """Test that highest severity is used when merging."""
        config = get_default_config()
        engine = CorrelationEngine(config)
        
        vuln1 = create_vulnerability_dict(
            title="Test vulnerability",
            description="Test",
            severity="medium",
            host="example.com",
            detected_by="tool1",
            cve_ids=["CVE-2024-1234"],
        )
        
        vuln2 = create_vulnerability_dict(
            title="Test vulnerability",
            description="Test",
            severity="critical",
            host="example.com",
            detected_by="tool2",
            cve_ids=["CVE-2024-1234"],
        )
        
        result = engine.correlate([vuln1, vuln2])
        
        assert len(result) == 1
        assert result[0]["severity"] == "critical"
