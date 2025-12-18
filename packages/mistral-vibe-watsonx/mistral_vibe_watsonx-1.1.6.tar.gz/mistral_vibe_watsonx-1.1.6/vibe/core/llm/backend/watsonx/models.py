"""WatsonX Model Discovery Service.

Fetches available models from WatsonX API for dynamic model selection.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from vibe.core.llm.backend.watsonx.auth import WatsonXAuth

# WatsonX API configuration
WATSONX_API_VERSION = "2024-05-31"
DEFAULT_TIMEOUT = 30.0


@dataclass
class WatsonXModel:
    """Represents a WatsonX model."""

    model_id: str
    label: str
    provider: str
    short_description: str
    tasks: list[str]


class WatsonXModelService:
    """Service for fetching available models from WatsonX."""

    def __init__(
        self,
        api_key: str,
        region: str = "us-south",
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the model service.

        Args:
            api_key: IBM Cloud IAM API key
            region: WatsonX region (us-south, eu-de, etc.)
            timeout: Request timeout in seconds
        """
        self._api_key = api_key
        self._region = region
        self._timeout = timeout
        self._base_url = f"https://{region}.ml.cloud.ibm.com"

    async def fetch_models(self) -> list[WatsonXModel]:
        """Fetch available foundation models from WatsonX.

        Returns:
            List of available models

        Raises:
            WatsonXAuthError: If authentication fails
            httpx.HTTPError: If the API request fails
        """
        auth = WatsonXAuth(self._api_key)

        async with auth:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                auth=auth,
                timeout=httpx.Timeout(self._timeout),
            ) as client:
                return await self._fetch_models_with_retry(client)

    async def _fetch_models_with_retry(
        self, client: httpx.AsyncClient
    ) -> list[WatsonXModel]:
        """Fetch models with retry logic."""
        url = f"/ml/v1/foundation_model_specs?version={WATSONX_API_VERSION}"

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
            reraise=True,
        ):
            with attempt:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return self._parse_models(data)

        return []  # Unreachable, but satisfies type checker

    def _parse_models(self, data: dict) -> list[WatsonXModel]:
        """Parse the API response into model objects."""
        models: list[WatsonXModel] = []

        resources = data.get("resources", [])
        for resource in resources:
            # Filter to models that support chat/generation
            tasks = resource.get("tasks", [])
            task_ids = [t.get("id", "") for t in tasks]

            # Only include models that can do generation or chat
            if not any(t in task_ids for t in ["generation", "chat"]):
                continue

            model = WatsonXModel(
                model_id=resource.get("model_id", ""),
                label=resource.get("label", resource.get("model_id", "")),
                provider=resource.get("provider", "unknown"),
                short_description=resource.get("short_description", ""),
                tasks=task_ids,
            )
            models.append(model)

        # Sort by provider then model_id
        models.sort(key=lambda m: (m.provider.lower(), m.model_id.lower()))
        return models


async def fetch_watsonx_models(
    api_key: str,
    region: str = "us-south",
) -> list[WatsonXModel]:
    """Convenience function to fetch WatsonX models.

    Args:
        api_key: IBM Cloud IAM API key
        region: WatsonX region

    Returns:
        List of available models
    """
    service = WatsonXModelService(api_key=api_key, region=region)
    return await service.fetch_models()