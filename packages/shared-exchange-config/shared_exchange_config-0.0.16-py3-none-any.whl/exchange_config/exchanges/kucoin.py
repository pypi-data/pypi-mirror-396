"""KuCoin exchange configuration."""

from typing import Dict, List
from .base import BaseExchangeConfig


class KucoinConfig(BaseExchangeConfig):
    """KuCoin exchange configuration with network mappings and deposit addresses."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))
    
    @property
    def networks_for_deposit_addresses(self) -> Dict[str, str]:
        """Get networks available for deposit addresses."""
        return dict(self._config.get("networks_for_deposit_addresses", {})) 
