"""
Alpha Vantage API Client - 원자재 모듈

이 모듈은 Alpha Vantage의 상품 데이터 API에 대한 접근을 제공합니다.
상품 API는 원유, 천연가스, 구리, 밀 등 주요 상품에 대한 과거 데이터를 제공하며,
다양한 시간 범위(일별, 주별, 월별, 분기별 등)를 아우릅니다.
"""

import logging
from typing import Any, Literal

from .base import BaseAPIHandler

logger = logging.getLogger(__name__)


class Commodities(BaseAPIHandler):
    """
    Commodities API handler for Alpha Vantage API

    This class provides access to commodities data including:
    - WTI (West Texas Intermediate crude oil)
    - BRENT (Brent crude oil)
    - NATURAL_GAS (Henry Hub natural gas)
    - COPPER (Global price of copper)
    - ALUMINUM (Global price of aluminum)
    - WHEAT (Global price of wheat)
    - CORN (Global price of corn)
    - COTTON (Global price of cotton)
    - SUGAR (Global price of sugar)
    - COFFEE (Global price of coffee)
    - ALL_COMMODITIES (Global price index of all commodities)
    """

    async def wti(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get West Texas Intermediate (WTI) crude oil prices

        This API returns the West Texas Intermediate (WTI) crude oil prices in daily,
        weekly, and monthly horizons.

        Args:
            interval: Time interval (daily, weekly, monthly). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            WTI crude oil price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.wti(interval="monthly")
        """
        params = {
            "function": "WTI",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def brent(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get Brent crude oil prices

        This API returns the Brent (Europe) crude oil prices in daily, weekly,
        and monthly horizons.

        Args:
            interval: Time interval (daily, weekly, monthly). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Brent crude oil price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.brent(interval="weekly")
        """
        params = {
            "function": "BRENT",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def natural_gas(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get Henry Hub natural gas spot prices

        This API returns the Henry Hub natural gas spot prices in daily, weekly,
        and monthly horizons.

        Args:
            interval: Time interval (daily, weekly, monthly). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Natural gas price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.natural_gas(interval="daily")
        """
        params = {
            "function": "NATURAL_GAS",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def copper(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price of copper

        This API returns the global price of copper in monthly, quarterly,
        and annual horizons.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Copper price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.copper(interval="quarterly")
        """
        params = {
            "function": "COPPER",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def aluminum(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price of aluminum

        This API returns the global price of aluminum in monthly, quarterly,
        and annual horizons.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Aluminum price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.aluminum(interval="annual")
        """
        params = {
            "function": "ALUMINUM",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def wheat(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price of wheat

        This API returns the global price of wheat in monthly, quarterly,
        and annual horizons.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Wheat price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.wheat(interval="monthly")
        """
        params = {
            "function": "WHEAT",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def corn(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price of corn

        This API returns the global price of corn in monthly, quarterly,
        and annual horizons.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Corn price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.corn(interval="quarterly")
        """
        params = {
            "function": "CORN",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def cotton(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price of cotton

        This API returns the global price of cotton in monthly, quarterly,
        and annual horizons.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Cotton price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.cotton(interval="annual")
        """
        params = {
            "function": "COTTON",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def sugar(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price of sugar

        This API returns the global price of sugar in monthly, quarterly,
        and annual horizons.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Sugar price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.sugar(interval="monthly")
        """
        params = {
            "function": "SUGAR",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def coffee(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price of coffee

        This API returns the global price of coffee in monthly, quarterly,
        and annual horizons.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Coffee price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.coffee(interval="quarterly")
        """
        params = {
            "function": "COFFEE",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    async def all_commodities(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get global price index of all commodities

        This API returns the global price index of all commodities in monthly,
        quarterly, and annual temporal dimensions.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly
            datatype: Output format (json, csv). Default: json

        Returns:
            Global commodities price index data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.commodities.all_commodities(interval="annual")
        """
        params = {
            "function": "ALL_COMMODITIES",
            "interval": interval,
            "datatype": datatype,
        }

        return await self.client._make_request(params)

    # Convenience methods for commonly requested commodities
    async def get_oil_prices(
        self,
        oil_type: Literal["wti", "brent"] = "wti",
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
    ) -> dict[str, Any]:
        """
        Get oil prices for WTI or Brent crude

        Convenience method to get oil price data.

        Args:
            oil_type: Type of oil (wti, brent). Default: wti
            interval: Time interval (daily, weekly, monthly). Default: monthly

        Returns:
            Oil price data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> wti_data = await client.commodities.get_oil_prices("wti", "daily")
            >>> brent_data = await client.commodities.get_oil_prices("brent", "weekly")
        """
        if oil_type == "wti":
            return await self.wti(interval=interval)
        elif oil_type == "brent":
            return await self.brent(interval=interval)
        else:
            raise ValueError("oil_type must be 'wti' or 'brent'")

    async def get_energy_commodities(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
    ) -> dict[str, dict[str, Any]]:
        """
        Get energy commodities data (WTI, Brent, Natural Gas)

        Convenience method to get multiple energy commodities data.

        Args:
            interval: Time interval (daily, weekly, monthly). Default: monthly

        Returns:
            Dictionary with energy commodities data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> energy_data = await client.commodities.get_energy_commodities("weekly")
            >>> wti_data = energy_data["wti"]
            >>> brent_data = energy_data["brent"]
            >>> gas_data = energy_data["natural_gas"]
        """
        return {
            "wti": await self.wti(interval=interval),
            "brent": await self.brent(interval=interval),
            "natural_gas": await self.natural_gas(interval=interval),
        }

    async def get_agricultural_commodities(
        self,
        interval: Literal["monthly", "quarterly", "annual"] = "monthly",
    ) -> dict[str, dict[str, Any]]:
        """
        Get agricultural commodities data (Wheat, Corn, Cotton, Sugar, Coffee)

        Convenience method to get multiple agricultural commodities data.

        Args:
            interval: Time interval (monthly, quarterly, annual). Default: monthly

        Returns:
            Dictionary with agricultural commodities data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> agri_data = await client.commodities.get_agricultural_commodities("quarterly")
            >>> wheat_data = agri_data["wheat"]
            >>> corn_data = agri_data["corn"]
            >>> cotton_data = agri_data["cotton"]
            >>> sugar_data = agri_data["sugar"]
            >>> coffee_data = agri_data["coffee"]
        """
        return {
            "wheat": await self.wheat(interval=interval),
            "corn": await self.corn(interval=interval),
            "cotton": await self.cotton(interval=interval),
            "sugar": await self.sugar(interval=interval),
            "coffee": await self.coffee(interval=interval),
        }
