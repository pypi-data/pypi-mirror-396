"""
Configuration management for Soren CLI
Handles local storage of credentials and settings
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class SorenConfig:
    """Manage Soren CLI configuration and credentials"""
    
    def __init__(self):
        """Initialize config manager with default config directory"""
        self.config_dir = Path.home() / ".soren"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from disk"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to disk"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Make config file readable only by user
        os.chmod(self.config_file, 0o600)
    
    def get_api_key(self) -> Optional[str]:
        """Get stored API key"""
        config = self.load()
        return config.get('api_key')
    
    def set_api_key(self, api_key: str) -> None:
        """Store API key"""
        config = self.load()
        config['api_key'] = api_key
        self.save(config)
    
    def get_api_url(self) -> Optional[str]:
        """Get configured API URL"""
        config = self.load()
        return config.get('api_url')
    
    def set_api_url(self, url: str) -> None:
        """Set API URL"""
        config = self.load()
        config['api_url'] = url
        self.save(config)
    
    def clear(self) -> None:
        """Clear all stored configuration"""
        if self.config_file.exists():
            self.config_file.unlink()
