"""
Exception classes for TokenVault SDK.
"""


class SDKConfigurationError(Exception):
    """
    Raised when SDK configuration is invalid or missing required values.
    
    This is a fail-fast error that should be raised during SDK initialization
    to prevent agents from starting with invalid configuration.
    """
    pass


class InsufficientBalanceError(Exception):
    """
    Raised when an organization's balance is below the configured threshold.
    
    This error prevents LLM API calls from being made when the organization
    doesn't have sufficient balance to cover the estimated cost.
    """
    pass


class TrackingError(Exception):
    """
    Raised when usage tracking fails.
    
    This is typically logged but not raised to avoid blocking agent responses.
    """
    pass
