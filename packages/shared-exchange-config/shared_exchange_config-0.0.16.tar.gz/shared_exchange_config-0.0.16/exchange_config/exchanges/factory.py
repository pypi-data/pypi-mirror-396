"""Factory for creating exchange-specific configuration classes."""

from typing import Dict, Any, Union
from pathlib import Path

from .base import BaseExchangeConfig
from .binance import BinanceConfig
from .kraken import KrakenConfig
from .bybit import BybitConfig
from .deribit import DeribitConfig
from .dydx import DydxConfig
from .bitfinex import BitfinexConfig
from .hitbtc import HitbtcConfig
from .hyperliquid import HyperliquidConfig
from .okx import OkxConfig
from .bitstamp import BitstampConfig
from .kucoin import KucoinConfig


# Mapping of exchange names to their specific config classes
EXCHANGE_CLASS_MAP = {
    "binance": BinanceConfig,
    "kraken": KrakenConfig,
    "bybit": BybitConfig,
    "deribit": DeribitConfig,
    "dydx": DydxConfig,
    "bitfinex": BitfinexConfig,
    "hitbtc": HitbtcConfig,
    "hyperliquid": HyperliquidConfig,
    "okx": OkxConfig,
    "bitstamp": BitstampConfig,
    "kucoin": KucoinConfig,
}


def create_exchange_config(exchange_name: str, config_data: Dict[str, Any]) -> BaseExchangeConfig:
    """
    Create the appropriate exchange config class based on exchange name.
    
    Args:
        exchange_name: Name of the exchange
        config_data: Configuration data dictionary
        
    Returns:
        Appropriate exchange config instance
    """
    config_class = EXCHANGE_CLASS_MAP.get(exchange_name, BaseExchangeConfig)
    return config_class(exchange_name, config_data)


def create_exchange_config_from_file(file_path: Union[str, Path]) -> BaseExchangeConfig:
    """
    Create exchange config from JSON file using the appropriate class.
    
    Args:
        file_path: Path to the JSON configuration file
        
    Returns:
        Appropriate exchange config instance
    """
    import json
    
    file_path = Path(file_path)
    exchange_name = file_path.stem
    
    with open(file_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    return create_exchange_config(exchange_name, config_data) 
