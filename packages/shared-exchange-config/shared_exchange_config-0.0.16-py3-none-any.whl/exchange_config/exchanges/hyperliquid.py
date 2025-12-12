"""Hyperliquid exchange configuration."""

from typing import Dict
from .base import BaseExchangeConfig


class HyperliquidConfig(BaseExchangeConfig):
    """Hyperliquid exchange configuration with simple network mappings."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))

    @property
    def alias_to_currency_map(self) -> Dict[str, str]:
        """Get alias to currency mapping."""
        return dict(self._config.get("alias_to_currency_map", {}))
