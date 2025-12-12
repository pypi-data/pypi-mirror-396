"""OKX exchange configuration."""

from typing import Dict
from .base import BaseExchangeConfig


class OkxConfig(BaseExchangeConfig):
    """OKX exchange configuration with network mappings."""
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {})) 