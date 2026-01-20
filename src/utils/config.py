import yaml
import os
from typing import Dict, Any
from loguru import logger

class ConfigLoader:
    def __init__(self, config_path: str = "config/system_configuration.yaml"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """Loads the configuration from the YAML file."""
        if not os.path.exists(self.config_path):
            logger.error(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully.")
            return self._config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    @property
    def remote_ip(self) -> str:
        return self._config.get("remote_ip", "")

    @property
    def username(self) -> str:
        return self._config.get("username", "")

    @property
    def key_file(self) -> str:
        return self._config.get("key_file", "")
