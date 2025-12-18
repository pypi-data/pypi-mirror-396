"""
Configuration module for TokenVault SDK.

Handles environment variable parsing and validation for SDK configuration.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SDKConfig:
    """
    Configuration for TokenVault SDK.
    
    All settings can be configured via environment variables with the TOKENVAULT_ prefix.
    """
    
    redis_url: str
    tokenvault_api_url: str
    stream_name: str = "usage_records"
    balance_threshold: float = 0.0
    cache_ttl: int = 60
    fail_open: bool = True
    max_retries: int = 3
    retry_backoff_ms: int = 100
    
    @classmethod
    def from_env(cls, prefix: str = "TOKENVAULT_") -> "SDKConfig":
        """
        Create configuration from environment variables.
        
        Args:
            prefix: Environment variable prefix (default: TOKENVAULT_)
            
        Returns:
            SDKConfig instance
            
        Raises:
            SDKConfigurationError: If required variables are missing or invalid
        """
        from tokenvault_sdk.exceptions import SDKConfigurationError
        
        # Required variables
        redis_url = os.getenv(f"{prefix}REDIS_URL")
        if not redis_url:
            raise SDKConfigurationError(
                f"Missing required environment variable: {prefix}REDIS_URL"
            )
        
        tokenvault_api_url = os.getenv(f"{prefix}API_URL")
        if not tokenvault_api_url:
            raise SDKConfigurationError(
                f"Missing required environment variable: {prefix}API_URL"
            )
        
        # Optional variables with defaults
        stream_name = os.getenv(f"{prefix}STREAM_NAME", "usage_records")
        
        # Parse numeric values with validation
        try:
            balance_threshold = float(
                os.getenv(f"{prefix}BALANCE_THRESHOLD", "0.0")
            )
        except ValueError as e:
            raise SDKConfigurationError(
                f"Invalid {prefix}BALANCE_THRESHOLD: must be a number"
            ) from e
        
        try:
            cache_ttl = int(os.getenv(f"{prefix}CACHE_TTL", "60"))
            if cache_ttl < 0:
                raise ValueError("cache_ttl must be non-negative")
        except ValueError as e:
            raise SDKConfigurationError(
                f"Invalid {prefix}CACHE_TTL: must be a non-negative integer"
            ) from e
        
        try:
            max_retries = int(os.getenv(f"{prefix}MAX_RETRIES", "3"))
            if max_retries < 0:
                raise ValueError("max_retries must be non-negative")
        except ValueError as e:
            raise SDKConfigurationError(
                f"Invalid {prefix}MAX_RETRIES: must be a non-negative integer"
            ) from e
        
        try:
            retry_backoff_ms = int(os.getenv(f"{prefix}RETRY_BACKOFF_MS", "100"))
            if retry_backoff_ms < 0:
                raise ValueError("retry_backoff_ms must be non-negative")
        except ValueError as e:
            raise SDKConfigurationError(
                f"Invalid {prefix}RETRY_BACKOFF_MS: must be a non-negative integer"
            ) from e
        
        # Parse boolean
        fail_open_str = os.getenv(f"{prefix}FAIL_OPEN", "true").lower()
        fail_open = fail_open_str in ("true", "1", "yes", "on")


        return cls(
            redis_url=redis_url,
            tokenvault_api_url=tokenvault_api_url,
            stream_name=stream_name,
            balance_threshold=balance_threshold,
            cache_ttl=cache_ttl,
            fail_open=fail_open,
            max_retries=max_retries,
            retry_backoff_ms=retry_backoff_ms,
        )
    
    def validate(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            SDKConfigurationError: If configuration is invalid
        """
        from tokenvault_sdk.exceptions import SDKConfigurationError
        
        if not self.redis_url:
            raise SDKConfigurationError("redis_url cannot be empty")
        
        if not self.tokenvault_api_url:
            raise SDKConfigurationError("tokenvault_api_url cannot be empty")
        
        if not self.stream_name:
            raise SDKConfigurationError("stream_name cannot be empty")
        
        if self.cache_ttl < 0:
            raise SDKConfigurationError("cache_ttl must be non-negative")
        
        if self.max_retries < 0:
            raise SDKConfigurationError("max_retries must be non-negative")
        
        if self.retry_backoff_ms < 0:
            raise SDKConfigurationError("retry_backoff_ms must be non-negative")
