"""Test configuration loading."""
import pytest
from pathlib import Path
from dutVulnScanner.core.config import (
    load_config,
    get_default_config,
    load_profile,
    get_profiles_dir,
)


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = get_default_config()
        
        assert "runners" in config
        assert "adapters" in config
        assert "reporting" in config
        assert "correlation" in config
    
    def test_load_config_without_file(self):
        """Test loading config when no file exists."""
        config = load_config()
        
        # Should return default config
        assert config is not None
        assert "runners" in config
    
    def test_profiles_dir_exists(self):
        """Test that profiles directory exists or can be created."""
        profiles_dir = get_profiles_dir()
        
        assert profiles_dir.exists()
        assert profiles_dir.is_dir()
    
    def test_load_web_profile(self):
        """Test loading web profile."""
        profile = load_profile("web")
        
        assert "tools" in profile
        assert "whatweb" in profile["tools"]
        assert "nuclei" in profile["tools"]
    
    def test_load_infra_profile(self):
        """Test loading infrastructure profile."""
        profile = load_profile("infra")
        
        assert "tools" in profile
        assert "nmap" in profile["tools"]
    
    def test_load_nonexistent_profile(self):
        """Test loading a profile that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_profile("nonexistent_profile")
