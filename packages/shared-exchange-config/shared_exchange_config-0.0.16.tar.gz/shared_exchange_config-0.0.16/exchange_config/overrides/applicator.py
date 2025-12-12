"""
Configuration applicator for applying overrides to exchange configurations.
"""

import warnings
from typing import Dict, Any


class ConfigurationApplicator:
    """Applies configuration overrides to exchange configurations."""
    
    @staticmethod
    def apply_overrides_to_exchange(exchange: 'BaseExchangeConfig', overrides: Dict[str, Any]):
        """
        Apply overrides to a single exchange configuration.
        
        Args:
            exchange: BaseExchangeConfig instance to modify
            overrides: Dictionary of overrides to apply
        """
        for operation, value in overrides.items():
            ConfigurationApplicator._apply_single_override(exchange, operation, value)
    
    @staticmethod
    def apply_global_overrides_to_exchange(exchange: 'BaseExchangeConfig', global_overrides: Dict[str, Any]):
        """
        Apply global overrides to a single exchange configuration.
        
        Args:
            exchange: BaseExchangeConfig instance to modify
            global_overrides: Dictionary of global overrides to apply
        """
        for operation, value in global_overrides.items():
            ConfigurationApplicator._apply_single_override(exchange, operation, value)
    
    @staticmethod
    def _apply_single_override(exchange: 'BaseExchangeConfig', operation: str, value: Any):
        """Apply a single override operation to an exchange."""
        
        if operation == 'add_currencies':
            currencies = value if isinstance(value, list) else [value]
            current_currencies = exchange.available_currencies
            for currency in currencies:
                if currency not in current_currencies:
                    current_currencies.append(currency)
            exchange.available_currencies = current_currencies
        
        elif operation == 'add_fiat_currencies':
            currencies = value if isinstance(value, list) else [value]
            current_fiat = exchange.available_fiat_currencies
            for currency in currencies:
                if currency not in current_fiat:
                    current_fiat.append(currency)
            exchange.available_fiat_currencies = current_fiat
        
        elif operation == 'remove_currencies':
            currencies = value if isinstance(value, list) else [value]
            current_currencies = exchange.available_currencies
            current_fiat = exchange.available_fiat_currencies
            currencies_to_networks_mapping = exchange.currencies_to_networks.copy()  # Make a copy to modify
            
            for currency in currencies:
                # Remove from crypto currencies
                if currency in current_currencies:
                    current_currencies.remove(currency)
                # Remove from fiat currencies
                if currency in current_fiat:
                    current_fiat.remove(currency)
                # Remove from networks mapping
                if currency in currencies_to_networks_mapping:
                    del currencies_to_networks_mapping[currency]
            
            exchange.available_currencies = current_currencies
            exchange.available_fiat_currencies = current_fiat
            exchange.set_config_field("currencies_to_networks", currencies_to_networks_mapping)
        
        elif operation == 'add_currency_networks':
            # Format: {"BTC": ["LIGHTNING"], "ETH": ["ARBITRUM"]}
            if isinstance(value, dict):
                currencies_to_networks_mapping = exchange.currencies_to_networks.copy()  # Make a copy to modify
                for currency, networks in value.items():
                    if currency in exchange.all_currencies:  # Only add if currency exists
                        network_list = networks if isinstance(networks, list) else [networks]
                        if currency not in currencies_to_networks_mapping:
                            currencies_to_networks_mapping[currency] = []
                        for network in network_list:
                            if network not in currencies_to_networks_mapping[currency]:
                                currencies_to_networks_mapping[currency].append(network)
                exchange.set_config_field("currencies_to_networks", currencies_to_networks_mapping)
        
        elif operation == 'add_networks':
            # Format: {"LIGHTNING": "lightning", "ARBITRUM": "arbitrum"} or {"SINGLE_NETWORK": "single"}
            if isinstance(value, dict):
                current_networks = exchange.get_config_field("networks", {})
                if not isinstance(current_networks, dict):
                    current_networks = {}
                else:
                    current_networks = current_networks.copy()  # Make a copy to modify
                for network_key, network_value in value.items():
                    current_networks[network_key] = network_value
                exchange.set_config_field("networks", current_networks)
        
        elif operation == 'add_currency_and_network_to_alias_map':
            # Format: {"BTC-LIGHTNING": "BTC_LN", "ETH-ARBITRUM": "ETH_ARB"}
            if isinstance(value, dict):
                alias_mapping = exchange.get_config_field("currency_and_network_to_alias_map", {})
                if not isinstance(alias_mapping, dict):
                    alias_mapping = {}
                else:
                    alias_mapping = alias_mapping.copy()  # Make a copy to modify
                for currency_network, alias in value.items():
                    alias_mapping[currency_network] = alias
                exchange.set_config_field("currency_and_network_to_alias_map", alias_mapping)
        
        elif operation.startswith('set_'):
            # Direct field setting: set_custom_field -> custom_field
            field_name = operation[4:]  # Remove 'set_' prefix
            exchange.set_config_field(field_name, value)
        
        else:
            # Unknown operation, log warning but don't fail
            warnings.warn(f"Unknown override operation: {operation}")
