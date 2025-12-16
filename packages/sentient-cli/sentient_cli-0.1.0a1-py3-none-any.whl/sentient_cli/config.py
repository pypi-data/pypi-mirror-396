"""
Configuration management for Sentient CLI
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class SentientConfig(BaseModel):
    """Configuration model for sentient.config.json"""
    
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    type: Literal["agent", "mcp"] = Field(..., description="Project type")
    framework: str = Field(..., description="AI framework used")
    visibility: Literal["public", "private"] = Field(default="private", description="Deployment visibility")
    runtime: Literal["python", "node"] = Field(default="python", description="Runtime environment")
    build_command: Optional[str] = Field(default=None, description="Build command")
    start_command: str = Field(..., description="Start command")
    port: int = Field(default=8000, description="Port number", ge=1, le=65535)
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate project name format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Project name cannot be empty")
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Project name can only contain letters, numbers, hyphens, and underscores")
        
        return v.strip()
    
    @field_validator('framework')
    @classmethod
    def validate_framework(cls, v: str) -> str:
        """Validate framework name"""
        valid_frameworks = {
            'langchain', 'crewai', 'autogen', 'openai', 'anthropic',
            'custom', 'fastapi', 'flask', 'django', 'mcp-server'
        }
        
        if v.lower() not in valid_frameworks:
            # Allow custom frameworks but warn
            pass
        
        return v.lower()
    
    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True
    )


class ConfigManager:
    """Manager for sentient.config.json file operations"""
    
    CONFIG_FILENAME = "sentient.config.json"
    
    def __init__(self, project_path: Optional[Path] = None):
        """
        Initialize config manager
        
        Args:
            project_path: Path to project directory (defaults to current directory)
        """
        self.project_path = project_path or Path.cwd()
        self.config_file = self.project_path / self.CONFIG_FILENAME
    
    def exists(self) -> bool:
        """Check if config file exists"""
        return self.config_file.exists()
    
    def load(self) -> SentientConfig:
        """
        Load configuration from file
        
        Returns:
            SentientConfig object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not self.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return SentientConfig(**data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load config: {e}")
    
    def save(self, config: SentientConfig) -> None:
        """
        Save configuration to file
        
        Args:
            config: SentientConfig object to save
        """
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict and save with pretty formatting
            config_dict = config.model_dump()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise ValueError(f"Failed to save config: {e}")
    
    def create_default(self, **overrides: Any) -> SentientConfig:
        """
        Create default configuration with optional overrides
        
        Args:
            **overrides: Values to override defaults
            
        Returns:
            SentientConfig with default values
        """
        defaults = {
            "name": self.project_path.name,
            "description": f"AI project: {self.project_path.name}",
            "type": "agent",
            "framework": "custom",
            "visibility": "private",
            "runtime": "python",
            "start_command": "python main.py",
            "port": 8000,
            "environment": {}
        }
        
        # Apply overrides
        defaults.update(overrides)
        
        return SentientConfig(**defaults)
    
    def update(self, **updates: Any) -> SentientConfig:
        """
        Update existing configuration
        
        Args:
            **updates: Fields to update
            
        Returns:
            Updated SentientConfig
        """
        config = self.load()
        
        # Update fields
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Validate and save
        config = SentientConfig(**config.model_dump())
        self.save(config)
        
        return config


def get_config_manager(project_path: Optional[Path] = None) -> ConfigManager:
    """
    Get a ConfigManager instance
    
    Args:
        project_path: Optional project path
        
    Returns:
        ConfigManager instance
    """
    return ConfigManager(project_path)