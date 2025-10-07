"""
Alpha Vantage API Client - Base Module
Common utilities and base functionality
"""

import logging
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    pass  # Remove circular import reference

logger = logging.getLogger(__name__)


class BaseAPIHandler:
    """Base class for API handlers"""

    def __init__(self, client: Any):  # Use Any to avoid circular import
        self.client = client

    @property
    def api_key(self) -> str:
        """Get API key from client"""
        return self.client.api_key

    @property
    def base_url(self) -> str:
        """Get base URL from client"""
        return self.client.BASE_URL

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        return await self.client._get_session()

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None or value == "None" or value == "":
            return default
        try:
            if isinstance(value, str):
                # Remove percentage sign and other common characters
                value = value.replace("%", "").replace(",", "").strip()
            return float(value)
        except (ValueError, TypeError):
            return default

    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int"""
        if value is None or value == "None" or value == "":
            return default
        try:
            if isinstance(value, str):
                value = value.replace(",", "").strip()
            return int(float(value))  # Convert to float first to handle decimal strings
        except (ValueError, TypeError):
            return default

    def _safe_str(self, value: Any, default: str = "") -> str:
        """Safely convert value to string"""
        if value is None or value == "None":
            return default
        return str(value).strip()

    async def _make_request(self, params: dict[str, Any]) -> dict[str, Any]:
        """Make API request with common error handling"""
        session = await self._get_session()

        try:
            async with session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                # Check for API errors
                if "Error Message" in data:
                    raise ValueError(
                        f"Alpha Vantage API Error: {data['Error Message']}"
                    )
                if "Note" in data:
                    raise ValueError(f"Alpha Vantage API Limit: {data['Note']}")

                return data

        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for request: {e}")
            raise
        except Exception as e:
            logger.error(f"Error for request: {e}")
            raise
