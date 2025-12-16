import asyncio
import json
import json.decoder
from dataclasses import dataclass
from enum import Enum
from typing import cast

import httpx
from arcade_tdk import ToolContext

from arcade_jira.constants import JIRA_API_VERSION, JIRA_BASE_URL, JIRA_MAX_CONCURRENT_REQUESTS
from arcade_jira.exceptions import NotFoundError


class APIType(str, Enum):
    """Enum for different Jira API types."""

    V3_REST = "v3_rest"
    AGILE = "agile"


@dataclass
class JiraClient:
    context: ToolContext
    cloud_id: str | None
    base_url: str = JIRA_BASE_URL
    api_version: str = JIRA_API_VERSION
    max_concurrent_requests: int = JIRA_MAX_CONCURRENT_REQUESTS
    # Type of API to use - V3_REST for standard operations, AGILE for sprint/board operations
    client_type: APIType = APIType.V3_REST
    _semaphore: asyncio.Semaphore | None = None

    @property
    def auth_token(self) -> str | None:
        return self.context.get_auth_token_or_empty()

    def __post_init__(self) -> None:
        if not self._semaphore:
            cached_semaphore = getattr(self.context, "_global_jira_client_semaphore", None)

            # If a semaphore was already cached in the context, we use it. Some tools
            # may call other tools. Each tool will instantiate its own JiraClient.
            # This is necessary to ensure that all instances will respect the
            # concurrency limit.
            if cached_semaphore:
                self._semaphore = cached_semaphore
            else:
                self._semaphore = asyncio.Semaphore(self.max_concurrent_requests)
                self.context._global_jira_client_semaphore = self._semaphore  # type: ignore[attr-defined]

        self.base_url = self.base_url.rstrip("/")
        self.api_version = self.api_version.strip("/")

    async def _build_url(self, endpoint: str) -> str:
        base_path = f"{self.base_url}/{self.cloud_id or ''}/rest"
        if self.client_type == APIType.AGILE:
            return f"{base_path}/agile/1.0/{endpoint.lstrip('/')}"
        else:
            return f"{base_path}/api/{self.api_version}/{endpoint.lstrip('/')}"

    async def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 404:
            message = "Resource not found"
            raise NotFoundError(message)

        response.raise_for_status()

    def _set_request_body(self, kwargs: dict, data: dict | None, json_data: dict | None) -> dict:
        if data and json_data:
            raise ValueError("Cannot provide both data and json_data")  # noqa: TRY003

        if data:
            kwargs["data"] = data

        elif json_data:
            kwargs["json"] = json_data

        return kwargs

    def _format_response_dict(self, response: httpx.Response) -> dict:
        try:
            return cast(dict, response.json())
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            return {"text": response.text}

    async def get(
        self,
        endpoint: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        default_headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/json",
        }
        headers = {**default_headers, **(headers or {})}

        kwargs = {
            "url": await self._build_url(endpoint),
            "headers": headers,
        }

        if params:
            kwargs["params"] = params

        async with self._semaphore, httpx.AsyncClient() as client:  # type: ignore[union-attr]
            response = await client.get(**kwargs)  # type: ignore[arg-type]
            await self._raise_for_status(response)

        return self._format_response_dict(response)

    async def post(
        self,
        endpoint: str,
        data: dict | None = None,
        json_data: dict | None = None,
        files: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        default_headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/json",
        }

        if files is None and json_data is not None:
            default_headers["Content-Type"] = "application/json"

        headers = {**default_headers, **(headers or {})}

        kwargs = {
            "url": await self._build_url(endpoint),
            "headers": headers,
        }

        if files is not None:
            kwargs["files"] = files
            if data is not None:
                kwargs["data"] = data
        else:
            kwargs = self._set_request_body(kwargs, data, json_data)

        async with self._semaphore, httpx.AsyncClient() as client:  # type: ignore[union-attr]
            response = await client.post(**kwargs)  # type: ignore[arg-type]
            await self._raise_for_status(response)

        return self._format_response_dict(response)

    async def put(
        self,
        endpoint: str,
        data: dict | None = None,
        json_data: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        headers = headers or {}
        headers["Authorization"] = f"Bearer {self.auth_token}"
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"

        kwargs = {
            "url": await self._build_url(endpoint),
            "headers": headers,
        }

        kwargs = self._set_request_body(kwargs, data, json_data)

        if params:
            kwargs["params"] = params

        async with self._semaphore, httpx.AsyncClient() as client:  # type: ignore[union-attr]
            response = await client.put(**kwargs)  # type: ignore[arg-type]
            await self._raise_for_status(response)

        return self._format_response_dict(response)
