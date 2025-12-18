"""WatsonX Authentication with automatic IAM token refresh.

Custom httpx Auth handler for IBM WatsonX with:
- Proactive token refresh (5-minute buffer before expiration)
- Reactive token refresh (on 401 responses)
- Thread-safe with asyncio.Lock
- Automatic retry logic with exponential backoff via tenacity
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
import time

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# HTTP status codes
HTTP_UNAUTHORIZED = 401


class WatsonXAuthError(Exception):
    """Raised when IAM token refresh fails."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


@dataclass
class TokenData:
    """IAM token data with expiration."""

    access_token: str
    expires_at: float  # Unix timestamp

    def is_expired(self, buffer_seconds: int = 300) -> bool:
        """Check if token is expired or will expire soon.

        Args:
            buffer_seconds: Buffer time before expiration (default 5 minutes)

        Returns:
            True if token should be refreshed
        """
        return time.time() >= (self.expires_at - buffer_seconds)


class WatsonXAuth(httpx.Auth):
    """Custom httpx Auth for IBM WatsonX with automatic token refresh.

    This auth handler:
    1. Obtains IAM tokens from IBM Cloud IAM service
    2. Proactively refreshes tokens 5 minutes before expiration
    3. Reactively refreshes on 401 responses
    4. Uses async lock for thread-safe token refresh
    5. Retries token refresh on transient failures
    """

    requires_response_body = True  # Enable reactive refresh on 401
    IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self, api_key: str) -> None:
        """Create WatsonX auth handler.

        Args:
            api_key: IBM Cloud IAM API key
        """
        self.api_key = api_key
        self._token: TokenData | None = None
        self._async_lock = asyncio.Lock()
        self._refresh_client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> WatsonXAuth:
        """Async context manager entry - create refresh client."""
        self._refresh_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=5),
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit - close refresh client."""
        if self._refresh_client:
            await self._refresh_client.aclose()
            self._refresh_client = None

    def sync_auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Synchronous auth flow - NOT SUPPORTED.

        WatsonXAuth requires AsyncClient because token refresh is async.
        """
        raise RuntimeError(
            "WatsonXAuth requires httpx.AsyncClient. "
            "Use 'async with httpx.AsyncClient(auth=auth)' instead."
        )
        yield request  # Never reached, satisfies type checker

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        """Asynchronous auth flow with token refresh.

        This implements the httpx auth flow:
        1. Check if token needs refresh (proactive)
        2. Add token to request
        3. Yield request
        4. Check response for 401 (reactive)
        5. Refresh and retry if needed
        """
        # Proactive refresh: check if token is expired or will expire soon
        if not self._token or self._token.is_expired():
            await self._refresh_token()

        # Add Bearer token to request
        if self._token:
            request.headers["Authorization"] = f"Bearer {self._token.access_token}"

        # Yield request and get response
        response = yield request

        # Reactive refresh: if we get 401, refresh and retry once
        if response.status_code == HTTP_UNAUTHORIZED:
            await self._refresh_token()

            # Update token in request and retry
            if self._token:
                request.headers["Authorization"] = f"Bearer {self._token.access_token}"
            yield request

    async def _refresh_token(self) -> None:
        """Refresh IAM token with double-check locking pattern.

        Uses tenacity for retry with exponential backoff.
        """
        async with self._async_lock:
            # Double-check: another coroutine may have already refreshed
            if self._token and not self._token.is_expired():
                return

            # Ensure we have a refresh client
            if not self._refresh_client:
                self._refresh_client = httpx.AsyncClient(
                    timeout=httpx.Timeout(30.0),
                    limits=httpx.Limits(max_connections=5),
                )

            try:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=2, max=10),
                    retry=retry_if_exception_type(httpx.HTTPError),
                    reraise=True,
                ):
                    with attempt:
                        response = await self._refresh_client.post(
                            self.IAM_TOKEN_URL,
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            data={
                                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                                "apikey": self.api_key,
                            },
                        )
                        response.raise_for_status()

                        data = response.json()
                        self._token = TokenData(
                            access_token=data["access_token"],
                            expires_at=data["expiration"],
                        )

            except Exception as error:
                raise WatsonXAuthError(
                    message="Failed to refresh IBM Cloud IAM token",
                    cause=error if isinstance(error, Exception) else None,
                ) from error

    async def get_token(self) -> str:
        """Get current access token, refreshing if needed.

        Returns:
            Current access token
        """
        if not self._token or self._token.is_expired():
            await self._refresh_token()

        if not self._token:
            raise WatsonXAuthError("No token available after refresh")

        return self._token.access_token