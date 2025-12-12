"""Manager class for handling multiple exchange configurations."""

from typing import Dict, List, Set
from pathlib import Path

from .exchanges import BaseExchangeConfig, create_exchange_config_from_file
from .exceptions import ExchangeNotFoundError
from .overrides import apply_startup_configuration


class ExchangeConfigManager:
    """Manager for multiple exchange configurations."""
    
    def __init__(self):
        """
        Initialize the exchange configuration manager with configurations from the data directory.
        """
        self.config_directory = Path(__file__).parent / "data"
        self._exchanges: Dict[str, BaseExchangeConfig] = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all JSON configuration files from the directory."""
        json_files = list(self.config_directory.glob("*.json"))
        
        for json_file in json_files:
            try:
                exchange_config = create_exchange_config_from_file(json_file)
                self._exchanges[exchange_config.exchange_name] = exchange_config
            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")
        
        # Apply startup configuration overrides
        self._exchanges = apply_startup_configuration(self._exchanges)
    
    def get_exchange_names(self) -> List[str]:
        """Get list of all available exchange names."""
        return list(self._exchanges.keys())

    def get_exchange(self, exchange_name: str) -> BaseExchangeConfig:
        """
        Get configuration for a specific exchange.
        
        Args:
            exchange_name: Name of the exchange
            
        Returns:
            BaseExchangeConfig instance
        """
        if exchange_name not in self._exchanges:
            raise ExchangeNotFoundError(exchange_name)
        
        return self._exchanges[exchange_name]
    
    def get_all_currencies(self) -> Set[str]:
        """Get all unique currencies across all exchanges."""
        all_currencies = set()
        for exchange in self._exchanges.values():
            all_currencies.update(exchange.all_currencies)
        return all_currencies
    
    def __repr__(self) -> str:
        """String representation of the manager."""
        return f"ExchangeConfigManager(exchanges={len(self._exchanges)}, directory='{self.config_directory}')" 
