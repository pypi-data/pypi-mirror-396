"""
Shared test utilities for exchange configuration override tests.
"""

import unittest
from unittest.mock import Mock, patch
import json
import warnings
from typing import Dict, List, Any

from exchange_config.exchanges.base import BaseExchangeConfig
from exchange_config.exceptions import ValidationError


class BaseOverrideTestCase(unittest.TestCase):
    """Base test case with common setup for override tests."""
    
    def get_test_exchange_config(self) -> BaseExchangeConfig:
        """Get a standard test exchange configuration."""
        test_config = {
            "available_currencies": ["BTC", "ETH", "ADA"],
            "available_fiat_currencies": ["USD", "EUR"],
            "currencies_to_networks": {
                "BTC": ["BITCOIN", "LIGHTNING"],
                "ETH": ["ETHEREUM"],
                "ADA": ["CARDANO"],
            },
            "networks": {
                "BITCOIN": "bitcoin",
                "LIGHTNING": "lightning"
            },
            "currency_and_network_to_alias_map": {
                "BTC-BITCOIN": "BTC_MAIN"
            },
            "custom_field": "original_value"
        }
        return BaseExchangeConfig("test_exchange", test_config) 