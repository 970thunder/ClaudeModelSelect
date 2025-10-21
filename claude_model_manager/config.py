"""
Configuration management for Claude Code models
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional


class ModelConfig:
    """Represents a single model configuration"""

    def __init__(self, name: str, base_url: str, model: str, api_key: str = ""):
        self.name = name
        self.base_url = base_url
        self.model = model
        self.api_key = api_key

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "base_url": self.base_url,
            "model": self.model,
            "api_key": self.api_key
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelConfig':
        """Create from dictionary"""
        return cls(
            name=data.get("name", ""),
            base_url=data.get("base_url", ""),
            model=data.get("model", ""),
            api_key=data.get("api_key", "")
        )


class ConfigManager:
    """Manages model configurations"""

    def __init__(self, config_file: Optional[str] = None):
        if config_file is None:
            self.config_file = Path.home() / ".claude_model_manager" / "config.json"
        else:
            self.config_file = Path(config_file)

        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.models: Dict[str, ModelConfig] = {}
        self.current_model: Optional[str] = None
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.models = {}
                for model_data in data.get("models", []):
                    model = ModelConfig.from_dict(model_data)
                    self.models[model.name] = model

                self.current_model = data.get("current_model")
            except (json.JSONDecodeError, KeyError, Exception) as e:
                print(f"Error loading config: {e}")
                self.models = {}
                self.current_model = None
        else:
            # Create default configuration
            self.models = {}
            self.current_model = None
            self.save_config()

    def save_config(self) -> None:
        """Save configuration to file"""
        data = {
            "models": [model.to_dict() for model in self.models.values()],
            "current_model": self.current_model
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_model(self, model: ModelConfig) -> bool:
        """Add a new model configuration"""
        if model.name in self.models:
            return False
        self.models[model.name] = model
        self.save_config()
        return True

    def update_model(self, old_name: str, model: ModelConfig) -> bool:
        """Update an existing model configuration"""
        if old_name not in self.models:
            return False

        # If name changed, remove old entry
        if old_name != model.name:
            del self.models[old_name]

        self.models[model.name] = model

        # Update current model if it was the one being updated
        if self.current_model == old_name:
            self.current_model = model.name

        self.save_config()
        return True

    def delete_model(self, name: str) -> bool:
        """Delete a model configuration"""
        if name not in self.models:
            return False

        del self.models[name]

        # Clear current model if it was the one being deleted
        if self.current_model == name:
            self.current_model = None

        self.save_config()
        return True

    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get a model configuration by name"""
        return self.models.get(name)

    def list_models(self) -> List[str]:
        """Get list of all model names"""
        return list(self.models.keys())

    def set_current_model(self, name: str) -> bool:
        """Set the current active model"""
        if name not in self.models:
            return False
        self.current_model = name
        self.save_config()
        return True

    def get_current_model(self) -> Optional[ModelConfig]:
        """Get the current active model"""
        if self.current_model:
            return self.models.get(self.current_model)
        return None

    def export_environment_vars(self) -> Dict[str, str]:
        """Export environment variables for the current model"""
        current = self.get_current_model()
        if not current:
            return {}

        env_vars = {
            "ANTHROPIC_BASE_URL": current.base_url,
            "ANTHROPIC_MODEL": current.model
        }

        if current.api_key:
            # 智能选择认证变量，避免冲突
            if "anthropic" in current.base_url.lower():
                # Anthropic官方API使用AUTH_TOKEN
                env_vars["ANTHROPIC_AUTH_TOKEN"] = current.api_key
                # 清理可能冲突的API_KEY
                env_vars["ANTHROPIC_API_KEY"] = ""
            else:
                # 其他厂商API使用API_KEY
                env_vars["ANTHROPIC_API_KEY"] = current.api_key
                # 清理可能冲突的AUTH_TOKEN
                env_vars["ANTHROPIC_AUTH_TOKEN"] = ""

        return env_vars