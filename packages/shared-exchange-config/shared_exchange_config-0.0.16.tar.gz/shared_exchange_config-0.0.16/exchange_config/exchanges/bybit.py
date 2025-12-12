"""Bybit exchange configuration."""

from typing import Dict, List
from .base import BaseExchangeConfig


class BybitConfig(BaseExchangeConfig):
    """Bybit exchange configuration with wallet types and network mappings."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))

