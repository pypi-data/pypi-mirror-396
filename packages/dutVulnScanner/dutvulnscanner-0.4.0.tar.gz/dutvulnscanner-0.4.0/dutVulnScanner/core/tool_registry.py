"""Tool registry - metadata and installation info for all security tools."""

import platform
from typing import Dict, Any, List, Optional
from enum import Enum


class ToolCategory(str, Enum):
    """Tool categories."""
    CORE = "core"  # Bắt buộc
    RECOMMENDED = "recommended"  # Nên có
    OPTIONAL = "optional"  # Tùy chọn, có thể nguy hiểm


class InstallMethod(str, Enum):
    """Installation methods."""
    APT = "apt"
    GO = "go"
    BINARY = "binary"
    MANUAL = "manual"


# Tool registry with metadata
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ==================== RECON TOOLS ====================
    "subfinder": {
        "category": ToolCategory.RECOMMENDED,
        "description": "Fast subdomain enumeration tool",
        "check_command": ["subfinder", "-version"],
        "type": "recon",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.GO,
                "go_package": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
                "binary_url": "https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_<version>_linux_amd64.zip",
                "apt_package": None,
            }
        },
        "homepage": "https://github.com/projectdiscovery/subfinder",
        "used_in_profiles": ["recon", "discovery_full", "full_scan"],
    },
    "naabu": {
        "category": ToolCategory.RECOMMENDED,
        "description": "Fast port scanner",
        "check_command": ["naabu", "-version"],
        "type": "recon",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.GO,
                "go_package": "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
                "binary_url": "https://github.com/projectdiscovery/naabu/releases/latest/download/naabu_<version>_linux_amd64.zip",
                "apt_package": None,
            }
        },
        "homepage": "https://github.com/projectdiscovery/naabu",
        "used_in_profiles": ["recon", "discovery_full", "full_scan", "infra"],
    },
    "httpx": {
        "category": ToolCategory.RECOMMENDED,
        "description": "Fast HTTP probe and tech detection",
        "check_command": ["httpx", "-version"],
        "type": "recon",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.GO,
                "go_package": "github.com/projectdiscovery/httpx/cmd/httpx@latest",
                "binary_url": "https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_<version>_linux_amd64.zip",
                "apt_package": None,
            }
        },
        "homepage": "https://github.com/projectdiscovery/httpx",
        "used_in_profiles": ["recon", "discovery_full", "full_scan", "web"],
    },
    "nmap": {
        "category": ToolCategory.CORE,
        "description": "Network mapper and service detection",
        "check_command": ["nmap", "--version"],
        "type": "recon",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.APT,
                "apt_package": "nmap",
                "go_package": None,
                "binary_url": None,
            }
        },
        "homepage": "https://nmap.org",
        "used_in_profiles": ["all"],  # Used in most profiles
    },
    "whatweb": {
        "category": ToolCategory.RECOMMENDED,
        "description": "Web technology fingerprinting",
        "check_command": ["whatweb", "--version"],
        "type": "recon",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.APT,
                "apt_package": "whatweb",
                "go_package": None,
                "binary_url": None,
            }
        },
        "homepage": "https://github.com/urbanadventurer/WhatWeb",
        "used_in_profiles": ["web", "discovery_full", "full_scan"],
    },
    "whois": {
        "category": ToolCategory.RECOMMENDED,
        "description": "Domain information lookup",
        "check_command": ["whois", "--version"],
        "type": "recon",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.APT,
                "apt_package": "whois",
                "go_package": None,
                "binary_url": None,
            }
        },
        "homepage": "https://linux.die.net/man/1/whois",
        "used_in_profiles": ["recon", "full_scan"],
    },
    
    # ==================== SCANNER TOOLS ====================
    "nuclei": {
        "category": ToolCategory.CORE,
        "description": "Fast vulnerability scanner based on templates",
        "check_command": ["nuclei", "-version"],
        "type": "scanner",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.GO,
                "go_package": "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
                "binary_url": "https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_<version>_linux_amd64.zip",
                "apt_package": None,
            }
        },
        "homepage": "https://github.com/projectdiscovery/nuclei",
        "used_in_profiles": ["web", "vuln_scan", "full_scan", "quick"],
        "post_install": "nuclei -update-templates",  # Update templates after install
    },
    "testssl": {
        "category": ToolCategory.RECOMMENDED,
        "description": "SSL/TLS security testing",
        "check_command": ["testssl.sh", "--version"],
        "type": "scanner",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.BINARY,
                "apt_package": "testssl.sh",
                "go_package": None,
                "binary_url": "https://github.com/drwetter/testssl.sh/archive/refs/heads/3.0.tar.gz",
            }
        },
        "homepage": "https://github.com/drwetter/testssl.sh",
        "used_in_profiles": ["web", "vuln_scan", "full_scan", "infra"],
    },
    "sslscan": {
        "category": ToolCategory.RECOMMENDED,
        "description": "SSL/TLS configuration scanner",
        "check_command": ["sslscan", "--version"],
        "type": "scanner",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.APT,
                "apt_package": "sslscan",
                "go_package": None,
                "binary_url": None,
            }
        },
        "homepage": "https://github.com/rbsec/sslscan",
        "used_in_profiles": ["web", "vuln_scan", "full_scan", "infra"],
    },
    "nikto": {
        "category": ToolCategory.RECOMMENDED,
        "description": "Web server vulnerability scanner",
        "check_command": ["nikto", "-Version"],
        "type": "scanner",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.APT,
                "apt_package": "nikto",
                "go_package": None,
                "binary_url": None,
            }
        },
        "homepage": "https://github.com/sullo/nikto",
        "used_in_profiles": ["web", "vuln_scan", "full_scan"],
    },
    
    # ==================== VALIDATOR TOOLS ====================
    "dalfox": {
        "category": ToolCategory.OPTIONAL,
        "description": "XSS vulnerability scanner",
        "check_command": ["dalfox", "version"],
        "type": "validator",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.GO,
                "go_package": "github.com/hahwul/dalfox/v2@latest",
                "binary_url": "https://github.com/hahwul/dalfox/releases/latest/download/dalfox_<version>_linux_amd64.tar.gz",
                "apt_package": None,
            }
        },
        "homepage": "https://github.com/hahwul/dalfox",
        "used_in_profiles": ["validators", "deep_test"],
        "warning": "⚠️  Validator tool - có thể gây tác động đến hệ thống",
    },
    "sqlmap": {
        "category": ToolCategory.OPTIONAL,
        "description": "SQL injection detection and exploitation",
        "check_command": ["sqlmap", "--version"],
        "type": "validator",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.APT,
                "apt_package": "sqlmap",
                "go_package": None,
                "binary_url": None,
            }
        },
        "homepage": "https://sqlmap.org",
        "used_in_profiles": ["validators", "deep_test"],
        "warning": "⚠️  Validator tool - có thể gây tác động đến hệ thống",
    },
    "hydra": {
        "category": ToolCategory.OPTIONAL,
        "description": "Network authentication brute forcer",
        "check_command": ["hydra", "-h"],
        "type": "validator",
        "install_methods": {
            "linux": {
                "primary": InstallMethod.APT,
                "apt_package": "hydra",
                "go_package": None,
                "binary_url": None,
            }
        },
        "homepage": "https://github.com/vanhauser-thc/thc-hydra",
        "used_in_profiles": ["validators", "deep_test"],
        "warning": "⚠️  Validator tool - có thể gây tác động đến hệ thống và có thể bị cấm",
    },
}


def get_tool_info(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get tool information from registry.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool info dictionary or None if not found
    """
    return TOOL_REGISTRY.get(tool_name.lower())


def get_all_tools() -> List[str]:
    """Get list of all tool names."""
    return list(TOOL_REGISTRY.keys())


def get_tools_by_category(category: ToolCategory) -> List[str]:
    """Get tools filtered by category."""
    return [
        name for name, info in TOOL_REGISTRY.items()
        if info["category"] == category
    ]


def get_tools_by_profile(profile_name: str) -> List[str]:
    """Get tools required by a specific profile."""
    tools = []
    for name, info in TOOL_REGISTRY.items():
        used_in = info.get("used_in_profiles", [])
        if profile_name in used_in or "all" in used_in:
            tools.append(name)
    return tools


def get_install_command(tool_name: str, method: Optional[InstallMethod] = None) -> Optional[str]:
    """
    Get installation command for a tool.
    
    Args:
        tool_name: Name of the tool
        method: Preferred installation method (if None, use primary)
        
    Returns:
        Installation command string or None
    """
    tool_info = get_tool_info(tool_name)
    if not tool_info:
        return None
    
    os_name = platform.system().lower()
    if os_name not in tool_info["install_methods"]:
        return None
    
    install_info = tool_info["install_methods"][os_name]
    
    # Use specified method or primary
    install_method = method or install_info.get("primary")
    
    if install_method == InstallMethod.APT:
        pkg = install_info.get("apt_package")
        if pkg:
            return f"sudo apt-get install -y {pkg}"
    
    elif install_method == InstallMethod.GO:
        pkg = install_info.get("go_package")
        if pkg:
            return f"go install -v {pkg}"
    
    elif install_method == InstallMethod.BINARY:
        url = install_info.get("binary_url")
        if url:
            return f"# Download from: {url}"
    
    return None


def get_core_tools() -> List[str]:
    """Get list of core (required) tools."""
    return get_tools_by_category(ToolCategory.CORE)


def get_recommended_tools() -> List[str]:
    """Get list of recommended tools."""
    return get_tools_by_category(ToolCategory.RECOMMENDED)


def get_optional_tools() -> List[str]:
    """Get list of optional tools."""
    return get_tools_by_category(ToolCategory.OPTIONAL)
