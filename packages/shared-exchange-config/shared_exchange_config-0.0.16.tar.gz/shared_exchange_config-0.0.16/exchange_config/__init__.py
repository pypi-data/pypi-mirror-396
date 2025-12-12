"""
Shared Exchange Configuration Library

A Python library for managing cryptocurrency exchange configurations,
providing clean access to exchange data and startup configuration capabilities.
"""

from .manager import ExchangeConfigManager
from .overrides import configure_exchanges
from .exceptions import (
    ExchangeConfigError,
    ExchangeNotFoundError,
    CurrencyNotFoundError,
    ValidationError
)

__version__ = "1.0.0"
__all__ = [
    "ExchangeConfigManager", 
    "configure_exchanges",
    "ExchangeConfigError",
    "ExchangeNotFoundError",
    "CurrencyNotFoundError",
    "ValidationError"
] 