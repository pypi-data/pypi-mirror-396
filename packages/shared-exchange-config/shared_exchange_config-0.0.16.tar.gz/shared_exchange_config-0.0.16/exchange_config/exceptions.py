"""Exception classes for the exchange configuration library."""


class ExchangeConfigError(Exception):
    """Base exception for all exchange configuration errors."""
    pass


class ExchangeNotFoundError(ExchangeConfigError):
    """Raised when an exchange is not found."""
    
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        super().__init__(f"Exchange '{exchange_name}' not found")


class CurrencyNotFoundError(ExchangeConfigError):
    """Raised when a currency is not found in an exchange."""
    
    def __init__(self, currency: str, exchange_name: str):
        self.currency = currency
        self.exchange_name = exchange_name
        super().__init__(f"Currency '{currency}' not found in exchange '{exchange_name}'")


class ValidationError(ExchangeConfigError):
    """Raised when configuration validation fails."""
    pass 