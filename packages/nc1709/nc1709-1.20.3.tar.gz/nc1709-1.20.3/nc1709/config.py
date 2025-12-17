"""
Configuration management for NC1709 CLI
"""
import os
import json
import copy
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Manages NC1709 configuration"""
    
    DEFAULT_CONFIG = {
        "models": {
            "reasoning": "deepseek-r1:latest",
            "coding": "qwen2.5-coder:32b",
            "tools": "qwen2.5:32b",
            "general": "qwen2.5:32b",
            "fast": "qwen2.5-coder:7b"
        },
        "ollama": {
            "base_url": "http://localhost:11434",
            "timeout": 120
        },
        "safety": {
            "confirm_writes": True,
            "confirm_commands": True,
            "confirm_destructive": True,
            "auto_backup": True,
            "backup_dir": "~/.nc1709/backups"
        },
        "execution": {
            "max_retries": 3,
            "command_timeout": 60,
            "allowed_commands": [
                "ls", "cat", "grep", "find", "git", "npm", "npx", "pip", "pip3",
                "python", "python3", "node", "go", "cargo", "docker", "kubectl",
                "make", "cmake", "rustc", "javac", "java", "mvn", "gradle",
                "pytest", "jest", "yarn", "pnpm", "brew", "apt", "yum",
                "echo", "pwd", "whoami", "date", "sleep", "touch", "mkdir", "cp", "mv"
            ],
            "blocked_commands": [
                "rm -rf /", "rm -rf /*", "rm -rf ~",
                "dd if=/dev/zero", "dd if=/dev/random",
                "mkfs", "fdisk", "format",
                ":(){:|:&};:", "fork bomb"
            ]
        },
        "memory": {
            "enabled": True,
            "vector_db_path": "~/.nc1709/memory/vectors",
            "conversation_history": 100
        },
        "ui": {
            "color": True,
            "verbose": False,
            "stream_output": True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration

        Args:
            config_path: Path to config file. Defaults to ~/.nc1709/config.json
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.nc1709/config.json")

        self.config_path = Path(config_path)
        # Use deep copy to avoid modifying the class-level DEFAULT_CONFIG
        self.config: Dict[str, Any] = copy.deepcopy(self.DEFAULT_CONFIG)
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration")
    
    def save(self) -> None:
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """Merge user configuration with defaults"""
        for key, value in user_config.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'models.reasoning')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'models.reasoning')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()
    
    def get_model_for_task(self, task_type: str) -> str:
        """Get the appropriate model for a task type
        
        Args:
            task_type: Type of task (reasoning, coding, tools, general, fast)
        
        Returns:
            Model name
        """
        return self.get(f"models.{task_type}", self.get("models.general"))


# Global configuration instance
_config: Optional[Config] = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
