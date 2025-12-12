"""Binance exchange configuration."""

from typing import Dict, List
from .base import BaseExchangeConfig


class BinanceConfig(BaseExchangeConfig):
    """Binance exchange configuration with network mappings."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))
    