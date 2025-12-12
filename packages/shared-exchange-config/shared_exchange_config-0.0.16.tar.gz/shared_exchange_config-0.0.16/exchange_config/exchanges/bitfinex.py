"""Bitfinex exchange configuration."""

from typing import Dict, List
from .base import BaseExchangeConfig


class BitfinexConfig(BaseExchangeConfig):
    """Bitfinex exchange configuration with special alias mappings and wallet features."""
    
    @property
    def currency_and_network_to_alias_map(self) -> Dict[str, str]:
        """Get currency-network to alias mapping."""
        return dict(self._config.get("currency_and_network_to_alias_map", {}))
    
    @property
    def wallet_type_exchange_deposit_address_available(self) -> List[str]:
        """Get wallet types with exchange deposit address available."""
        return list(self._config.get("wallet_type_exchange_deposit_address_available", []))
    
    @property
    def currency_mapping_reversed(self) -> Dict[str, str]:
        """Get reversed currency mapping."""
        return dict(self._config.get("currency_mapping_reversed", {}))
    
    @property
    def fee_alias_to_currency_network_map(self) -> Dict[str, str]:
        """Get fee alias to currency network mapping."""
        return dict(self._config.get("fee_alias_to_currency_network_map", {})) 

    @property
    def tx_history_static_deposit_addresses(self) -> Dict[str, str]:
        """Get tx history static deposit addresses."""
        return dict(self._config.get("tx_history_static_deposit_addresses", {}))
