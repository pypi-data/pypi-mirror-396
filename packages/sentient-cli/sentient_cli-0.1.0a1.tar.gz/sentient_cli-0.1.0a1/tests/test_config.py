"""
Tests for configuration management
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import ValidationError

from sentient_cli.config import SentientConfig, ConfigManager


class TestSentientConfig:
    """Test SentientConfig model"""
    
    def test_valid_config(self):
        """Test creating a valid configuration"""
        config = SentientConfig(
            name="test-agent",
            description="Test AI agent",
            type="agent",
            framework="langchain",
            start_command="python main.py"
        )
        
        assert config.name == "test-agent"
        assert config.type == "agent"
        assert config.framework == "langchain"
        assert config.visibility == "private"  # default
        assert config.runtime == "python"  # default
        assert config.port == 8000  # default
    
    def test_invalid_name(self):
        """Test validation of invalid names"""
        with pytest.raises(ValidationError):
            SentientConfig(
                name="",  # empty name
                description="Test",
                type="agent",
                framework="custom",
                start_command="python main.py"
            )
    
    def test_framework_validation(self):
        """Test framework validation"""
        # Valid framework
        config = SentientConfig(
            name="test",
            description="Test",
            type="agent",
            framework="LangChain",  # should be lowercased
            start_command="python main.py"
        )
        assert config.framework == "langchain"


class TestConfigManager:
    """Test ConfigManager functionality"""
    
    def test_config_file_operations(self):
        """Test saving and loading configuration"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manager = ConfigManager(project_path)
            
            # Initially no config
            assert not manager.exists()
            
            # Create and save config
            config = SentientConfig(
                name="test-project",
                description="Test project",
                type="mcp",
                framework="custom",
                start_command="python server.py",
                port=9000,
                environment={"DEBUG": "true"}
            )
            
            manager.save(config)
            assert manager.exists()
            
            # Load and verify
            loaded_config = manager.load()
            assert loaded_config.name == "test-project"
            assert loaded_config.type == "mcp"
            assert loaded_config.port == 9000
            assert loaded_config.environment == {"DEBUG": "true"}
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manager = ConfigManager(project_path)
            
            with pytest.raises(FileNotFoundError):
                manager.load()