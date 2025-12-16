"""Schema definitions and validation for DUTVulnScanner."""
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


class SeverityLevel(str, Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityStatus(str, Enum):
    """Vulnerability status."""
    OPEN = "open"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    FIXED = "fixed"
    ACCEPTED = "accepted"


class Vulnerability(BaseModel):
    """Vulnerability model."""
    id: str = Field(..., description="Unique vulnerability ID")
    title: str = Field(..., description="Vulnerability title")
    description: str = Field(..., description="Detailed description")
    severity: SeverityLevel = Field(..., description="Severity level")
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="CVSS score")
    cve_ids: List[str] = Field(default_factory=list, description="Related CVE IDs")
    cwe_ids: List[str] = Field(default_factory=list, description="Related CWE IDs")
    status: VulnerabilityStatus = Field(default=VulnerabilityStatus.OPEN)
    
    # Location information
    host: str = Field(..., description="Target host")
    port: Optional[int] = Field(None, description="Target port")
    protocol: Optional[str] = Field(None, description="Protocol (tcp/udp)")
    service: Optional[str] = Field(None, description="Service name")
    
    # Detection information
    detected_by: str = Field(..., description="Tool that detected this vulnerability")
    detection_time: str = Field(..., description="ISO format timestamp")
    
    # Additional data
    evidence: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Evidence data")
    references: List[str] = Field(default_factory=list, description="Reference URLs")
    remediation: Optional[str] = Field(None, description="Remediation advice")
    
    @validator('cvss_score')
    def validate_cvss(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('CVSS score must be between 0 and 10')
        return v


class ScanResult(BaseModel):
    """Complete scan result model."""
    scan_id: str = Field(..., description="Unique scan ID")
    target: str = Field(..., description="Scan target")
    profile: str = Field(..., description="Profile used")
    start_time: str = Field(..., description="Scan start time (ISO format)")
    end_time: Optional[str] = Field(None, description="Scan end time (ISO format)")
    duration: Optional[float] = Field(None, description="Scan duration in seconds")
    
    vulnerabilities: List[Vulnerability] = Field(default_factory=list)
    
    # Metadata
    tools_used: List[str] = Field(default_factory=list)
    runner_type: str = Field(..., description="Runner used (local/ssh/docker)")
    status: str = Field(default="completed", description="Scan status")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    # Statistics
    statistics: Dict[str, Any] = Field(default_factory=dict)


class ScanProfile(BaseModel):
    """Scan profile configuration."""
    name: str = Field(..., description="Profile name")
    description: str = Field(..., description="Profile description")
    tools: List[str] = Field(..., description="Tools to use")
    
    # Tool-specific configurations
    tool_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Scan parameters
    parallel: bool = Field(default=True, description="Run tools in parallel")
    timeout: int = Field(default=3600, description="Timeout in seconds")
    
    # Correlation settings
    enable_correlation: bool = Field(default=True)
    
    @validator('tools')
    def validate_tools(cls, v):
        if not v:
            raise ValueError('At least one tool must be specified')
        return v


def validate_profile(profile_name: str) -> Tuple[bool, List[str]]:
    """
    Validate a scan profile.
    
    Args:
        profile_name: Name of the profile to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    from dutVulnScanner.core.config import load_profile
    
    errors = []
    
    try:
        profile_data = load_profile(profile_name)
        
        # Validate using Pydantic model
        try:
            ScanProfile(**profile_data)
        except Exception as e:
            errors.append(f"Schema validation failed: {str(e)}")
        
        # Additional validations
        if "tools" in profile_data:
            tools = profile_data["tools"]
            if not isinstance(tools, list):
                errors.append("'tools' must be a list")
            elif len(tools) == 0:
                errors.append("At least one tool must be specified")
        else:
            errors.append("Missing required field: 'tools'")
        
    except FileNotFoundError as e:
        errors.append(str(e))
    except Exception as e:
        errors.append(f"Error loading profile: {str(e)}")
    
    return len(errors) == 0, errors


def create_vulnerability_dict(
    title: str,
    description: str,
    severity: str,
    host: str,
    detected_by: str,
    **kwargs
) -> Dict[str, Any]:
    """Helper function to create a vulnerability dictionary."""
    from datetime import datetime
    
    vuln = {
        "id": kwargs.get("id", f"{detected_by}-{hash(title) % 10000}"),
        "title": title,
        "description": description,
        "severity": severity,
        "host": host,
        "detected_by": detected_by,
        "detection_time": datetime.utcnow().isoformat(),
        **kwargs
    }
    
    return vuln
