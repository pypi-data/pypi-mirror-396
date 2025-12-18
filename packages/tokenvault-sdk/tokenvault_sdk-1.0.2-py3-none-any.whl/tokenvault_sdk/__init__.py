"""
TokenVault SDK - Agent Usage Tracking Library

A lightweight Python SDK for AI agents to track LLM usage and forward billing data to TokenVault.
Provides simple functions for balance checking and usage tracking without wrapping your LLM client.
"""

from tokenvault_sdk.config import SDKConfig
from tokenvault_sdk.tracker import UsageTracker
from tokenvault_sdk.exceptions import (
    InsufficientBalanceError,
    SDKConfigurationError,
    TrackingError,
)
from tokenvault_sdk.logging_config import configure_logging, get_logger

__version__ = "1.0.2"
__all__ = [
    "SDKConfig",
    "UsageTracker",
    "InsufficientBalanceError",
    "SDKConfigurationError",
    "TrackingError",
    "configure_logging",
    "get_logger",
    "quickstart",
]


async def quickstart(organization_id: str, agent_name: str = "agent") -> tuple[UsageTracker, str]:
    import uuid
    import asyncio
    import httpx
    from .config import SDKConfig
    from .tracker import UsageTracker

    config = SDKConfig.from_env()
    tracker = UsageTracker(redis_url=config.redis_url, tokenvault_api_url=config.tokenvault_api_url)

    profile_id = f"agent_{agent_name}_{uuid.uuid4().hex[:8]}"

    async def _create_org():
        try:
            async with httpx.AsyncClient(timeout=3.0) as c:
                await c.post(
                    f"{config.tokenvault_api_url}/v1/wallet/organizations",
                    json={"id": organization_id, "name": organization_id}
                )
        except:
            pass 

    asyncio.create_task(_create_org())

    return tracker, profile_id
