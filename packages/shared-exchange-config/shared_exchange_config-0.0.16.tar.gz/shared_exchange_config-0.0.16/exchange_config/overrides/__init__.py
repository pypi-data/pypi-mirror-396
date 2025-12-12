"""
Configuration overrides management for exchange configurations.

This module handles all aspects of configuration overrides including:
- Loading overrides from various sources (environment, files, dictionaries)
- Applying overrides to exchange configurations
"""

from typing import Dict

from exchange_config.overrides.settings_parser import overrides_settings
from exchange_config.overrides.applicator import ConfigurationApplicator


__all__ = [
    'configure_exchanges',
    'apply_startup_configuration',
]


def configure_exchanges(**kwargs):
    """
    Configure exchange settings from various sources.
    Call this once at application startup.
    
    Keyword Args:
        config_file: Path to configuration file
        config_dict: Configuration dictionary
        override_dir: Directory with override files
        env_prefix: Environment variable prefix
        load_env: Whether to load from environment (default: True)
    
    Example for Django settings.py:
        from exchange_config import configure_exchanges
        
        configure_exchanges(
            config_dict=EXCHANGE_OVERRIDES,
            config_file='/path/to/overrides.json'
        )
    
    Example for FastAPI:
        from exchange_config import configure_exchanges
        
        @app.on_event("startup")
        async def startup_event():
            configure_exchanges(load_env=True)
    """
    # Clear previous settings
    overrides_settings.clear()
    
    # Load from environment by default
    if kwargs.get('load_env', True):
        env_prefix = kwargs.get('env_prefix', 'EXCHANGE_CONFIG_')
        overrides_settings.load_from_environment(env_prefix)
    
    # Load from file if provided
    if 'config_file' in kwargs and kwargs['config_file'] is not None:
        overrides_settings.load_from_file(kwargs['config_file'])
    
    # Load from dictionary if provided (Django/FastAPI settings)
    if 'config_dict' in kwargs:
        overrides_settings.load_from_dict(kwargs['config_dict'])
    
    # Load from override directory if provided
    if 'override_dir' in kwargs:
        overrides_settings.load_from_directory(kwargs['override_dir'])


def apply_startup_configuration(exchanges: Dict[str, 'BaseExchangeConfig']) -> Dict[str, 'BaseExchangeConfig']:
    """
    Apply all configured overrides to the loaded exchange configurations.
    
    This should be called once at application startup after loading the default
    configurations but before the application starts serving requests.
    
    Args:
        exchanges: Dictionary of exchange_name -> BaseExchangeConfig
    """
    applicator = ConfigurationApplicator()
    
    # Apply global overrides to all exchanges
    global_overrides = overrides_settings.get_global_overrides()
    if global_overrides:
        for exchange in exchanges.values():
            applicator.apply_global_overrides_to_exchange(exchange, global_overrides)
    
    # Apply exchange-specific overrides
    for exchange_name, exchange in exchanges.items():
        exchange_overrides = overrides_settings.get_exchange_overrides(exchange_name)
        if exchange_overrides:
            applicator.apply_overrides_to_exchange(exchange, exchange_overrides)
    
    return exchanges
