"""Base exchange configuration class with common properties."""

import json
import copy
from typing import Dict, List, Any, Union
from pathlib import Path


class BaseExchangeConfig:
    """Base class for all exchange configurations."""
    
    def __init__(self, exchange_name: str, config_data: Dict[str, Any]):
        """
        Initialize exchange configuration.
        
        Args:
            exchange_name: Name of the exchange
            config_data: Dictionary containing the exchange configuration
        """
        self.exchange_name = exchange_name
        self._config = copy.deepcopy(config_data)
    
    @classmethod
    def from_json_file(cls, file_path: Union[str, Path]) -> "BaseExchangeConfig":
        """
        Create config from a JSON file.
        
        Args:
            file_path: Path to the JSON configuration file
            
        Returns:
            BaseExchangeConfig instance
        """
        file_path = Path(file_path)
        exchange_name = file_path.stem
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        return cls(exchange_name, config_data)
    
    @property
    def available_currencies(self) -> List[str]:
        """Get list of available cryptocurrencies."""
        return list(self._config.get("available_currencies", []))
    
    @available_currencies.setter
    def available_currencies(self, value: List[str]):
        """Set available cryptocurrencies."""
        self._config["available_currencies"] = list(value)
    
    @property
    def available_fiat_currencies(self) -> List[str]:
        """Get list of available fiat currencies."""
        return list(self._config.get("available_fiat_currencies", []))
    
    @available_fiat_currencies.setter
    def available_fiat_currencies(self, value: List[str]):
        """Set available fiat currencies."""
        self._config["available_fiat_currencies"] = list(value)
    
    @property
    def all_currencies(self) -> List[str]:
        """Get all currencies (crypto + fiat)."""
        return self.available_currencies + self.available_fiat_currencies
    
    @property
    def currencies_to_networks(self) -> Dict[str, List[str]]:
        """Get currency to networks mapping."""
        return dict(self._config.get("currencies_to_networks", {}))
    
    # Wallet Type Methods
    def get_wallet_types(self) -> List[str]:
        """Get available wallet types."""
        return list(self._config.get("wallet_types", []))
    
    @property
    def wallet_type_to_currencies(self) -> Dict[str, List[str]]:
        """Get wallet type to currencies mapping."""
        return dict(self._config.get("wallet_type_to_currencies", {}))

    def get_wallet_currencies(self, wallet_type: str) -> List[str]:
        """Get currencies available for a specific wallet type."""
        return list(self.wallet_type_to_currencies.get(wallet_type, []))
    
    def __repr__(self) -> str:
        """String representation of the configuration."""
        currencies_count = len(self.all_currencies)
        currrencies_to_networks_count = len(self.currencies_to_networks)
        return f"{self.__class__.__name__}(exchange='{self.exchange_name}', currencies={currencies_count}, currrencies_to_networks={currrencies_to_networks_count})" 

    # Generic access methods
    def get_config_field(self, field_name: str, default: Any = None) -> Any:
        """Get any configuration field."""
        return self._config.get(field_name, default)
    
    def set_config_field(self, field_name: str, value: Any):
        """Set any configuration field."""
        self._config[field_name] = value
    
    def has_config_field(self, field_name: str) -> bool:
        """Check if configuration field exists."""
        return field_name in self._config
    
    # Export and reset methods
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return copy.deepcopy(self._config)