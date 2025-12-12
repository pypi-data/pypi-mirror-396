"""
Integration tests for exchange configuration overrides system.
"""

from tests.test_utils import BaseOverrideTestCase
from exchange_config.exchanges.base import BaseExchangeConfig
from exchange_config.overrides import (
    configure_exchanges,
    apply_startup_configuration,
)
from exchange_config.overrides.settings_parser import overrides_settings as settings


class TestIntegrationScenarios(BaseOverrideTestCase):
    """Test complex integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        settings.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        settings.clear()
    
    def test_complete_workflow(self):
        """Test complete workflow: configure -> validate -> apply."""
        # Step 1: Configure with comprehensive overrides
        config_dict = {
            "exchanges": {
                "binance": {
                    "add_currencies": ["CUSTOM_BINANCE"],
                    "add_currency_networks": {"BTC": ["LIGHTNING"]},
                    "set_custom_setting": "binance_value"
                },
                "kraken": {
                    "remove_currencies": ["OLD_TOKEN"],
                    "add_fiat_currencies": ["NOK"]
                }
            },
            "global": {
                "add_currencies": ["UNIVERSAL_TOKEN"],
                "set_global_flag": True
            }
        }
        
        # Step 2: Configure exchanges
        configure_exchanges(config_dict=config_dict, load_env=False)
        
        # Step 3: Create test exchanges
        exchanges = {
            "binance": BaseExchangeConfig("binance", {
                "available_currencies": ["BTC", "ETH"],
                "available_fiat_currencies": ["USD"],
                "currencies_to_networks": {"BTC": ["BITCOIN"]},
                "custom_setting": "original"
            }),
            "kraken": BaseExchangeConfig("kraken", {
                "available_currencies": ["BTC", "OLD_TOKEN"],
                "available_fiat_currencies": ["USD", "EUR"]
            })
        }
        
        # Step 4: Apply configuration
        result_exchanges = apply_startup_configuration(exchanges)
        
        # Step 5: Verify results
        binance = result_exchanges["binance"]
        
        # Check binance specific overrides
        self.assertEqual(binance.available_currencies, ["BTC", "ETH", "UNIVERSAL_TOKEN", "CUSTOM_BINANCE"])
        self.assertEqual(binance.currencies_to_networks["BTC"], ["BITCOIN", "LIGHTNING"])
        self.assertEqual(binance.get_config_field("custom_setting"), "binance_value")
        
        # Check global overrides applied to binance
        self.assertEqual(binance.get_config_field("global_flag"), True)
        
        # Check kraken specific overrides
        kraken = result_exchanges["kraken"]
        self.assertEqual(kraken.available_currencies, ["BTC", "UNIVERSAL_TOKEN"])  # OLD_TOKEN removed, UNIVERSAL_TOKEN added
        self.assertEqual(kraken.available_fiat_currencies, ["USD", "EUR", "NOK"])  # NOK added
        
        # Check global overrides applied to kraken
        self.assertEqual(kraken.get_config_field("global_flag"), True)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test empty configuration
        configure_exchanges(config_dict={}, load_env=False)
        
        exchanges = {
            "test": BaseExchangeConfig("test", {"available_currencies": ["BTC"]})
        }
        result = apply_startup_configuration(exchanges)
        self.assertEqual(result["test"].available_currencies, ["BTC"])  # Unchanged
        
        # Test configuration with empty sections
        config_dict = {
            "exchanges": {},
            "global": {}
        }
        configure_exchanges(config_dict=config_dict, load_env=False)
        
        result = apply_startup_configuration(exchanges)
        self.assertEqual(result["test"].available_currencies, ["BTC"])  # Still unchanged
    
    def test_complex_network_mapping_workflow(self):
        """Test complex network mapping and currency management workflow."""
        # Complex configuration with multiple operations
        config_dict = {
            "exchanges": {
                "binance": {
                    "add_currencies": ["USDT", "USDC"],
                    "add_currency_networks": {
                        "USDT": ["TRC20", "ERC20"],
                        "USDC": ["ERC20", "POLYGON"]
                    },
                    "add_networks": {
                        "TRC20": "tron",
                        "POLYGON": "polygon"
                    },
                    "add_currency_and_network_to_alias_map": {
                        "USDT-TRC20": "USDT_TRON",
                        "USDC-POLYGON": "USDC_POLY"
                    },
                    "remove_currencies": ["ADA"]
                }
            },
            "global": {
                "add_fiat_currencies": ["JPY", "GBP"],
                "set_api_version": "v2"
            }
        }
        
        # Configure
        configure_exchanges(config_dict=config_dict, load_env=False)
        
        # Create exchange with initial config
        exchange = BaseExchangeConfig("binance", {
            "available_currencies": ["BTC", "ETH", "ADA"],
            "available_fiat_currencies": ["USD", "EUR"],
            "currencies_to_networks": {
                "BTC": ["BITCOIN"],
                "ETH": ["ETHEREUM"]
            },
            "networks": {
                "BITCOIN": "bitcoin",
                "ETHEREUM": "ethereum"
            },
            "currency_and_network_to_alias_map": {
                "BTC-BITCOIN": "BTC_MAIN"
            }
        })
        
        exchanges = {"binance": exchange}
        result_exchanges = apply_startup_configuration(exchanges)
        binance = result_exchanges["binance"]
        
        # Verify currency changes
        self.assertEqual(binance.available_currencies, ["BTC", "ETH", "USDT", "USDC"])  # ADA removed, USDT/USDC added
        
        # Verify network mappings
        networks_mapping = binance.currencies_to_networks
        self.assertEqual({
            "BTC": ["BITCOIN"],
            "ETH": ["ETHEREUM"],
            "USDT": ["TRC20", "ERC20"],
            "USDC": ["ERC20", "POLYGON"],
        }, networks_mapping)
        
        # Verify network definitions
        networks = binance.get_config_field("networks")
        self.assertEqual({
            "TRC20": "tron",
            "POLYGON": "polygon",
            "BITCOIN": "bitcoin",
            "ETHEREUM": "ethereum"
        }, networks)
        
        # Verify alias mappings
        alias_map = binance.get_config_field("currency_and_network_to_alias_map")
        self.assertEqual({
            "USDT-TRC20": "USDT_TRON",
            "USDC-POLYGON": "USDC_POLY",
            "BTC-BITCOIN": "BTC_MAIN"
        }, alias_map)
        
        # Verify global overrides
        self.assertEqual(binance.available_fiat_currencies, ["USD", "EUR", "JPY", "GBP"])
        self.assertEqual(binance.get_config_field("api_version"), "v2")
    
    def test_multi_exchange_complex_scenario(self):
        """Test applying different configurations to multiple exchanges."""
        config_dict = {
            "exchanges": {
                "binance": {
                    "add_currencies": ["BINANCE_SPECIAL"],
                    "set_trading_fees": 0.001
                },
                "kraken": {
                    "add_currencies": ["KRAKEN_SPECIAL"],
                    "remove_currencies": ["EUR"],
                    "set_trading_fees": 0.002
                },
                "bybit": {
                    "add_fiat_currencies": ["CHF"],
                    "set_is_derivative": True
                }
            },
            "global": {
                "add_currencies": ["GLOBAL_COIN"],
                "set_compliance_level": "high"
            }
        }
        
        configure_exchanges(config_dict=config_dict, load_env=False)
        
        # Create multiple exchanges
        exchanges = {
            "binance": BaseExchangeConfig("binance", {
                "available_currencies": ["BTC", "ETH"],
                "available_fiat_currencies": ["USD", "EUR"]
            }),
            "kraken": BaseExchangeConfig("kraken", {
                "available_currencies": ["BTC"],
                "available_fiat_currencies": ["USD", "EUR", "GBP"]
            }),
            "bybit": BaseExchangeConfig("bybit", {
                "available_currencies": ["BTC"],
                "available_fiat_currencies": ["USD"]
            })
        }
        
        result_exchanges = apply_startup_configuration(exchanges)
        
        # Verify binance
        binance = result_exchanges["binance"]
        self.assertEqual(binance.available_currencies, ["BTC", "ETH", "GLOBAL_COIN", "BINANCE_SPECIAL"])
        self.assertEqual(binance.available_fiat_currencies, ["USD", "EUR"])
        self.assertEqual(binance.get_config_field("trading_fees"), 0.001)
        self.assertEqual(binance.get_config_field("compliance_level"), "high")  # Global
        
        # Verify kraken
        kraken = result_exchanges["kraken"]
        self.assertEqual(kraken.available_currencies, ["BTC", "GLOBAL_COIN", "KRAKEN_SPECIAL"])
        self.assertEqual(kraken.available_fiat_currencies, ["USD", "GBP"])  # EUR removed
        self.assertEqual(kraken.get_config_field("trading_fees"), 0.002)
        
        # Verify bybit
        bybit = result_exchanges["bybit"]
        self.assertEqual(bybit.available_currencies, ["BTC", "GLOBAL_COIN"])
        self.assertEqual(bybit.available_fiat_currencies, ["USD", "CHF"])
        self.assertEqual(bybit.get_config_field("is_derivative"), True)
        self.assertEqual(bybit.get_config_field("compliance_level"), "high")  # Global


if __name__ == '__main__':
    import unittest
    unittest.main() 