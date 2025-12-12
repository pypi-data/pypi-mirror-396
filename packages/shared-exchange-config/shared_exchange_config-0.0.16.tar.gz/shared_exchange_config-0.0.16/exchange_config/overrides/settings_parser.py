"""
Configuration parsing and settings management for exchange overrides.
"""

import os
import json
from typing import Dict, Any, Union
from pathlib import Path

from exchange_config.exceptions import ValidationError


class ExchangeOverridesConfigSettings:
    """Manages configuration settings and overrides for exchange configurations."""
    
    def __init__(self):
        self.overrides: Dict[str, Dict[str, Any]] = {}
        self.global_overrides: Dict[str, Any] = {}
    
    def load_from_environment(self, prefix: str = "EXCHANGE_CONFIG_"):
        """
        Load configuration overrides from environment variables.
        
        Environment variables should be in format:
        EXCHANGE_CONFIG_BINANCE_ADD_CURRENCIES=BTC,ETH,CUSTOM_TOKEN
        EXCHANGE_CONFIG_BINANCE_REMOVE_CURRENCIES=OLDTOKEN
        EXCHANGE_CONFIG_GLOBAL_ADD_CURRENCIES=NEWGLOBALTOKEN
        
        Args:
            prefix: Environment variable prefix
        """
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            
            # Remove prefix and parse
            config_key = key[len(prefix):].lower()
            parts = config_key.split('_', 1)
            
            if len(parts) < 2:
                continue
                
            exchange_or_global = parts[0]
            operation = parts[1]
            
            # Parse the value (JSON, comma-separated list, or single value)
            value = value.strip()
            
            # Try to parse as JSON first (for complex structures like dictionaries)
            if value.startswith('{') and value.endswith('}'):
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as string
                    parsed_value = value
            elif value.startswith('[') and value.endswith(']'):
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    # If JSON parsing fails, fall back to comma-separated parsing
                    if ',' in value:
                        parsed_value = [v.strip() for v in value.split(',')]
                    else:
                        parsed_value = value
            elif ',' in value:
                # Comma-separated list
                parsed_value = [v.strip() for v in value.split(',')]
            else:
                # Single value
                parsed_value = value
            
            if exchange_or_global == 'global':
                self.global_overrides[operation] = parsed_value
            else:
                exchange_name = exchange_or_global
                if exchange_name not in self.overrides:
                    self.overrides[exchange_name] = {}
                self.overrides[exchange_name][operation] = parsed_value
    
    def load_from_file(self, config_file: Union[str, Path]):
        """
        Load configuration overrides from a JSON/YAML file.
        
        Expected format:
        {
            "exchanges": {
                "binance": {
                    "add_currencies": ["CUSTOM_TOKEN"],
                    "remove_currencies": ["OLD_TOKEN"],
                    "add_fiat_currencies": ["GBP"]
                },
                "kraken": {
                    "add_currencies": ["ANOTHER_TOKEN"]
                }
            },
            "global": {
                "add_currencies": "GLOBAL_TOKEN"
            }
        }
        
        Args:
            config_file: Path to configuration file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                # Could add YAML support here if needed
                raise ValidationError(f"Unsupported config file format: {config_path.suffix}")
        
        # Load exchange-specific overrides
        if 'exchanges' in config_data:
            for exchange_name, exchange_overrides in config_data['exchanges'].items():
                if exchange_name not in self.overrides:
                    self.overrides[exchange_name] = {}
                self.overrides[exchange_name].update(exchange_overrides)
        
        # Load global overrides
        if 'global' in config_data:
            self.global_overrides.update(config_data['global'])
    
    def load_from_dict(self, config_dict: Dict[str, Any]):
        """
        Load configuration overrides from a dictionary.
        Useful for Django/FastAPI settings integration.
        
        Args:
            config_dict: Configuration dictionary
        """
        if 'exchanges' in config_dict:
            for exchange_name, exchange_overrides in config_dict['exchanges'].items():
                if exchange_name not in self.overrides:
                    self.overrides[exchange_name] = {}
                self.overrides[exchange_name].update(exchange_overrides)
        
        if 'global' in config_dict:
            self.global_overrides.update(config_dict['global'])
    
    def load_from_directory(self, override_dir: Union[str, Path]):
        """
        Load configuration overrides from JSON files in a directory.
        Each file should be named {exchange_name}.json with overrides.
        
        Args:
            override_dir: Directory containing override files
        """
        override_path = Path(override_dir)
        if not override_path.exists():
            return
        
        for json_file in override_path.glob('*.json'):
            exchange_name = json_file.stem
            
            with open(json_file, 'r', encoding='utf-8') as f:
                override_data = json.load(f)
            
            if exchange_name not in self.overrides:
                self.overrides[exchange_name] = {}
            self.overrides[exchange_name].update(override_data)
    
    def get_exchange_overrides(self, exchange_name: str) -> Dict[str, Any]:
        """Get overrides for a specific exchange."""
        return self.overrides.get(exchange_name, {})
    
    def get_global_overrides(self) -> Dict[str, Any]:
        """Get global overrides that apply to all exchanges."""
        return self.global_overrides
    
    def clear(self):
        """Clear all loaded overrides."""
        self.overrides.clear()
        self.global_overrides.clear()


overrides_settings = ExchangeOverridesConfigSettings()
