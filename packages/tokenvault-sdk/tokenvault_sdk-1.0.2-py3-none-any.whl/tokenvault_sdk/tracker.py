"""
Usage tracking module for TokenVault SDK.

Provides core functionality for credit balance checking and usage tracking.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import httpx
import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from tokenvault_sdk.exceptions import InsufficientBalanceError, TrackingError

logger = logging.getLogger(__name__)


class UsageTracker:
    """
    Core component for credit balance checking and usage tracking.

    Manages Redis connections, credit balance caching, and usage record publishing.
    """
    
    def __init__(
        self,
        redis_url: str,
        tokenvault_api_url: str,
        stream_name: str = "usage_records",
        balance_threshold: float = 0.0,
        cache_ttl: int = 60,
        fail_open: bool = True,
        max_retries: int = 3,
        retry_backoff_ms: int = 100,
    ):
        """
        Initialize UsageTracker.
        
        Args:
            redis_url: Redis connection URL
            tokenvault_api_url: TokenVault API base URL
            stream_name: Redis stream name for usage records
            balance_threshold: Minimum balance required for requests
            cache_ttl: Balance cache TTL in seconds
            fail_open: Whether to allow requests when services are unavailable
            max_retries: Maximum number of retry attempts
            retry_backoff_ms: Initial backoff delay in milliseconds
        """
        self.redis_url = redis_url
        self.tokenvault_api_url = tokenvault_api_url.rstrip('/')
        self.stream_name = stream_name
        self.balance_threshold = balance_threshold
        self.cache_ttl = cache_ttl
        self.fail_open = fail_open
        self.max_retries = max_retries
        self.retry_backoff_ms = retry_backoff_ms
        
        # Redis client (lazy initialization)
        self._redis_client: Optional[redis.Redis] = None
        self._redis_lock = asyncio.Lock()
        
        # HTTP client for TokenVault API
        self._http_client: Optional[httpx.AsyncClient] = None

        logger.debug(
            "UsageTracker initialized",
            extra={
                "redis_url": redis_url,
                "tokenvault_api_url": tokenvault_api_url,
            }
        )
    
    async def _get_redis_client(self) -> redis.Redis:
        """
        Get or create Redis client with connection pooling.
        
        Returns:
            Redis client instance
            
        Raises:
            RedisError: If connection fails and fail_open is False
        """
        if self._redis_client is None:
            async with self._redis_lock:
                if self._redis_client is None:
                    try:
                        self._redis_client = redis.from_url(
                            self.redis_url,
                            encoding="utf-8",
                            decode_responses=True,
                            max_connections=10,
                        )
                        # Test connection
                        await self._redis_client.ping()
                        logger.debug("Redis connection established")
                    except (RedisError, RedisConnectionError) as e:
                        logger.error(f"Failed to connect to Redis: {e}")
                        if not self.fail_open:
                            raise
                        # Return a client anyway for fail-open mode
                        self._redis_client = redis.from_url(
                            self.redis_url,
                            encoding="utf-8",
                            decode_responses=True,
                            max_connections=10,
                        )
        
        return self._redis_client
    
    async def _check_redis_health(self) -> bool:
        """
        Check Redis connection health.
        
        Returns:
            True if Redis is healthy, False otherwise
        """
        try:
            client = await self._get_redis_client()
            await client.ping()
            return True
        except (RedisError, RedisConnectionError) as e:
            logger.warning(f"Redis health check failed: {e}")
            return False
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client for TokenVault API.
        
        Returns:
            HTTP client instance
        """
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                follow_redirects=True,
            )
        return self._http_client
    
    async def close(self) -> None:
        """
        Close all connections gracefully.
        
        Should be called when shutting down the application.
        """
        if self._redis_client is not None:
            await self._redis_client.close()
            logger.debug("Redis connection closed")
        
        if self._http_client is not None:
            await self._http_client.aclose()
            logger.debug("HTTP client closed")

    async def check_credit_balance(
        self,
        organization_id: str,
        force_refresh: bool = False,
    ) -> float:
        """
        Check organization credit balance with Redis caching.

        First checks Redis cache for credit balance. If not found or force_refresh is True,
        fetches from TokenVault API and updates cache.

        Args:
            organization_id: Organization identifier
            force_refresh: Force fetch from Wallet API, bypassing cache

        Returns:
            Current credit balance as float

        Raises:
            InsufficientBalanceError: If credit balance is below threshold

        Note:
            In fail_open mode, returns infinity on errors to allow requests.
            In fail_closed mode, raises exception on errors.
        """
        start_time = time.time()
        cache_key = f"credit_balance:{organization_id}"
        balance: Optional[float] = None
        cached = False

        # Try to get from cache first (unless force_refresh)
        if not force_refresh:
            try:
                client = await self._get_redis_client()
                cached_value = await client.get(cache_key)
                if cached_value is not None:
                    balance = float(cached_value)
                    cached = True
            except (RedisError, RedisConnectionError, ValueError) as e:
                logger.debug(f"Redis cache read failed, falling back to TokenVault API: {e}")
                # Continue to fetch from API

        # Fetch from Wallet API if not in cache
        if balance is None:
            try:
                balance = await self._fetch_credit_balance_from_api(organization_id)
                cached = False

                # Update cache
                try:
                    client = await self._get_redis_client()
                    await client.setex(cache_key, self.cache_ttl, str(balance))
                except (RedisError, RedisConnectionError) as e:
                    logger.debug(f"Failed to update credit balance cache: {e}")
                    # Non-fatal, continue

            except Exception as e:
                logger.error(f"TokenVault API request failed: {e}")

                # Try to use stale cached balance if available
                stale_balance = await self._get_stale_cached_credit_balance(organization_id)
                if stale_balance is not None:
                    balance = stale_balance
                elif self.fail_open:
                    return float('inf')  # Allow request
                else:
                    raise InsufficientBalanceError(
                        f"Cannot verify credit balance for organization {organization_id}"
                    )
        
        # Validate credit balance against threshold
        if balance < self.balance_threshold:
            logger.warning(
                f"Insufficient credit balance for org {organization_id}: "
                f"{balance} < {self.balance_threshold}",
                extra={
                    "organization_id": organization_id,
                    "credit_balance": balance,
                    "threshold": self.balance_threshold,
                }
            )
            raise InsufficientBalanceError(
                f"Organization {organization_id} has insufficient credit balance: "
                f"{balance} < {self.balance_threshold}"
            )
        
        return balance
    
    async def _get_stale_cached_credit_balance(self, organization_id: str) -> Optional[float]:
        """
        Try to get stale cached credit balance (ignoring TTL).

        This is used as a fallback when Wallet API is unavailable.

        Args:
            organization_id: Organization identifier

        Returns:
            Cached credit balance if available, None otherwise
        """
        cache_key = f"credit_balance:{organization_id}"
        try:
            client = await self._get_redis_client()
            cached_value = await client.get(cache_key)
            if cached_value is not None:
                return float(cached_value)
        except (RedisError, RedisConnectionError, ValueError) as e:
            logger.debug(
                f"Could not retrieve stale cached credit balance: {e}",
                extra={"organization_id": organization_id}
            )
        return None
    
    async def _fetch_credit_balance_from_api(self, organization_id: str) -> float:
        """
        Fetch credit balance from TokenVault API.

        Args:
            organization_id: Organization identifier

        Returns:
            Current credit balance as float

        Raises:
            Exception: If API request fails
        """
        http_client = await self._get_http_client()
        # Note: balance endpoint lives under /v1/balance/organizations/{org_id}
        url = f"{self.tokenvault_api_url}/v1/balance/organizations/{organization_id}"

        try:
            response = await http_client.get(url)
            response.raise_for_status()
            data = response.json()
            # TokenVault API returns balance in credits with "balance" key
            credit_balance = float(data.get("balance", 0.0))
            return credit_balance
        except httpx.HTTPStatusError as e:
            logger.error(f"TokenVault API returned error: {e.response.status_code}")
            raise
        except (httpx.RequestError, ValueError) as e:
            logger.error(f"Failed to fetch credit balance from TokenVault API: {e}")
            raise

    async def track_usage(
        self,
        groq_response: Dict[str, Any],
        organization_id: str,
        profile_id: str,
        user_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Track LLM usage and publish to Redis Stream.
        
        Extracts metadata from Groq response, publishes to Redis Stream,
        and invalidates balance cache. This method is designed to be called
        in a fire-and-forget manner (via asyncio.create_task).
        
        Args:
            groq_response: Response from Groq API
            organization_id: Organization identifier
            profile_id: Agent/profile identifier
            user_id: User identifier (optional)
            metadata: Additional metadata (optional)
            
        Note:
            Errors are logged but not raised to avoid blocking agent responses.
        """
        start_time = time.time()
        
        try:
            # Extract metadata from Groq response
            usage_record = self._extract_usage_metadata(
                groq_response=groq_response,
                organization_id=organization_id,
                profile_id=profile_id,
                user_id=user_id,
                metadata=metadata,
            )
            
            # Publish to Redis Stream
            await self._publish_usage_record(usage_record)
            
            # Invalidate credit balance cache
            await self._invalidate_credit_balance_cache(organization_id)
            
        except Exception as e:
            # Log error but don't raise - tracking failures shouldn't block responses
            logger.error(
                f"Failed to track usage: {e}",
                extra={
                    "organization_id": organization_id,
                }
            )
    
    def _extract_usage_metadata(
        self,
        groq_response: Dict[str, Any],
        organization_id: str,
        profile_id: str,
        user_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extract usage metadata from Groq response.
        
        Args:
            groq_response: Response from Groq API
            organization_id: Organization identifier
            profile_id: Agent/profile identifier
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Dictionary containing usage record fields
        """
        # Extract usage data
        usage = groq_response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        
        # Extract purpose from response content (first 200 chars)
        purpose = ""
        choices = groq_response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            purpose = content[:200] if content else ""
        
        # Generate unique ID for the usage record
        import uuid
        record_id = str(uuid.uuid4())

        # Build usage record in the format expected by TokenVault backend
        usage_record = {
            "id": record_id,
            "organization_id": organization_id,
            "profile_id": profile_id,
            "user_id": user_id,
            "groq_request_id": groq_response.get("id", record_id),  # Use generated ID if not present
            "model": groq_response.get("model", ""),
            "prompt_tokens": prompt_tokens,  # Keep as integers
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "timestamp": int(time.time()),  # Unix timestamp in seconds
        }

        # Add metadata if provided (keep as dict; avoid stringifying to preserve JSON)
        if metadata:
            usage_record["metadata"] = metadata
        
        return usage_record
    
    async def _publish_usage_record(self, usage_record: Dict[str, Any]) -> None:
        """
        Publish usage record to Redis Stream with retry logic.
        
        Args:
            usage_record: Usage record dictionary
            
        Note:
            In fail_open mode, logs errors without raising exceptions.
            In fail_closed mode, raises TrackingError after retries exhausted.
        """
        import json

        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(
                multiplier=self.retry_backoff_ms / 1000.0,
                min=self.retry_backoff_ms / 1000.0,
                max=10.0,
            ),
            retry=retry_if_exception_type((RedisError, RedisConnectionError)),
            reraise=True,
        )
        async def _publish_with_retry():
            client = await self._get_redis_client()
            # Redis XADD needs field values as bytes/str/int/float, so serialize any complex types.
            payload = {}
            for k, v in usage_record.items():
                if isinstance(v, (dict, list)):
                    payload[k] = json.dumps(v)
                else:
                    payload[k] = v

            message_id = await client.xadd(self.stream_name, payload)
            return message_id
        
        try:
            await _publish_with_retry()
        except (RedisError, RedisConnectionError) as e:
            logger.error(
                f"Failed to publish usage record after {self.max_retries} retries: {e}",
                extra={"organization_id": usage_record.get("organization_id")}
            )
            # In fail_open mode, log error but don't raise
            # In fail_closed mode, raise to signal tracking failure
            if not self.fail_open:
                raise TrackingError(f"Failed to publish usage record: {e}")
    
    async def track_bfl_consumption(
        self,
        organization_id: str,
        profile_id: str,
        model: str,
        bfl_credits: float,
        record_id: str,
        user_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Track BFL (Black Forest Labs) image generation consumption.
        
        This method directly calls the TokenVault consumption API to track
        BFL Flux-2 image generation costs. Unlike track_usage which publishes
        to Redis streams, this makes a direct HTTP call to ensure immediate
        balance deduction.
        
        Args:
            organization_id: Organization identifier
            profile_id: Profile identifier
            model: Model name (e.g., "flux-2-pro", "flux-2-flex")
            bfl_credits: BFL credits charged (1 BFL credit = $0.01)
            record_id: Generation request ID
            user_id: User identifier (optional)
            metadata: Additional metadata (optional)
            
        Raises:
            InsufficientBalanceError: If balance is insufficient
            TrackingError: If consumption tracking fails
            
        Example:
            >>> tracker = UsageTracker(redis_url, tokenvault_url)
            >>> await tracker.track_bfl_consumption(
            ...     organization_id="org_123",
            ...     profile_id="profile_123",
            ...     model="flux-2-pro",
            ...     bfl_credits=4.5,
            ...     record_id="gen_abc123"
            ... )
        """
        start_time = time.time()
        
        try:
            http_client = await self._get_http_client()
            url = f"{self.tokenvault_api_url}/v1/consumption/process"
            
            # Build payload
            payload = {
                "organization_id": organization_id,
                "profile_id": profile_id,
                "model": model,
                "prompt_tokens": 0,  # Not applicable for image generation
                "completion_tokens": 0,
                "record_id": record_id,
                "user_id": user_id,
                "bfl_credits": bfl_credits,
                "metadata": metadata or {},
            }
            
            # Make request
            response = await http_client.post(url, json=payload)
            
            # Handle errors
            if response.status_code == 400:
                error_data = response.json()
                if "insufficient" in error_data.get("message", "").lower():
                    raise InsufficientBalanceError(
                        f"Insufficient balance for BFL consumption: {error_data.get('message')}"
                    )
                raise TrackingError(f"Invalid request: {error_data.get('message')}")
            
            response.raise_for_status()
            
            # Invalidate cache after successful consumption
            await self._invalidate_credit_balance_cache(organization_id)
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(
                f"BFL consumption tracked successfully in {elapsed_ms:.2f}ms",
                extra={
                    "organization_id": organization_id,
                    "model": model,
                    "bfl_credits": bfl_credits,
                    "record_id": record_id,
                }
            )
            
        except InsufficientBalanceError:
            raise  # Re-raise balance errors
        except httpx.HTTPStatusError as e:
            logger.error(f"TokenVault API error: {e.response.status_code} - {e.response.text}")
            raise TrackingError(f"Failed to track BFL consumption: {e}")
        except Exception as e:
            logger.error(f"Failed to track BFL consumption: {e}")
            if not self.fail_open:
                raise TrackingError(f"Failed to track BFL consumption: {e}")

    
    async def _invalidate_credit_balance_cache(self, organization_id: str) -> None:
        """
        Invalidate credit balance cache for organization.

        Args:
            organization_id: Organization identifier
        """
        cache_key = f"credit_balance:{organization_id}"
        try:
            client = await self._get_redis_client()
            await client.delete(cache_key)
        except (RedisError, RedisConnectionError) as e:
            logger.debug(f"Failed to invalidate credit balance cache: {e}")
            # Non-fatal, continue

