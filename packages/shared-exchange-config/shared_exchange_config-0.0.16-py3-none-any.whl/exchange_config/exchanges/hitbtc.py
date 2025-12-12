"""HitBTC exchange configuration."""

from typing import Dict
from .base import BaseExchangeConfig


class HitbtcConfig(BaseExchangeConfig):
    """HitBTC exchange configuration with network mappings and aliases."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))
    
    @property
    def currency_and_network_to_alias_map(self) -> Dict[str, str]:
        """Get currency-network to alias mapping."""
        return dict(self._config.get("currency_and_network_to_alias_map", {})) 