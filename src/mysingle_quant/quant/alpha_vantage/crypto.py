"""
Alpha Vantage API Client - Digital & Crypto Currencies Module
"""

import logging
from typing import Any, Literal, Optional

from .base import BaseAPIHandler

logger = logging.getLogger(__name__)


class DigitalCryptoCurrencies(BaseAPIHandler):
    """
    Digital & Crypto Currencies API Handler

    This class provides access to Alpha Vantage's Digital & Crypto Currencies APIs,
    including currency exchange rates, intraday data, and historical time series
    for cryptocurrency and digital currency pairs.
    """

    async def currency_exchange_rate(
        self, from_currency: str, to_currency: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Get realtime exchange rate for any pair of cryptocurrency or physical currency.

        Args:
            from_currency: The currency you would like to get the exchange rate for.
                          It can either be a physical currency or cryptocurrency.
                          For example: 'USD' or 'BTC'.
            to_currency: The destination currency for the exchange rate.
                        It can either be a physical currency or cryptocurrency.
                        For example: 'USD' or 'BTC'.
            **kwargs: Additional parameters passed to the API.

        Returns:
            Dict containing the realtime exchange rate data.

        Example:
            >>> # Bitcoin to Euro
            >>> result = await client.crypto.currency_exchange_rate(
            ...     from_currency="BTC",
            ...     to_currency="EUR"
            ... )

            >>> # US Dollar to Japanese Yen
            >>> result = await client.crypto.currency_exchange_rate(
            ...     from_currency="USD",
            ...     to_currency="JPY"
            ... )
        """
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            **kwargs,
        }
        return await self.client._make_request(params)

    async def crypto_intraday(
        self,
        symbol: str,
        market: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"],
        outputsize: Optional[Literal["compact", "full"]] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get intraday time series data for cryptocurrency.

        Note: This is a premium API function.

        Args:
            symbol: The cryptocurrency of your choice. It can be any of the "from"
                   currencies in the cryptocurrency list. For example: 'ETH'.
            market: The exchange market of your choice. It can be any of the "to"
                   currencies in the cryptocurrency list. For example: 'USD'.
            interval: Time interval between two consecutive data points.
                     The following values are supported: '1min', '5min', '15min', '30min', '60min'
            outputsize: By default, 'compact'. Strings 'compact' and 'full' are accepted.
                       'compact' returns only the latest 100 data points;
                       'full' returns the full-length intraday time series.
            **kwargs: Additional parameters passed to the API.

        Returns:
            Dict containing the intraday time series data.

        Example:
            >>> # Ethereum intraday data in USD market
            >>> result = await client.crypto.crypto_intraday(
            ...     symbol="ETH",
            ...     market="USD",
            ...     interval="5min"
            ... )
        """
        params = {
            "function": "CRYPTO_INTRADAY",
            "symbol": symbol,
            "market": market,
            "interval": interval,
            **kwargs,
        }
        if outputsize is not None:
            params["outputsize"] = outputsize

        return await self.client._make_request(params)

    async def digital_currency_daily(
        self, symbol: str, market: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Get daily historical time series for a cryptocurrency traded on a specific market.

        This API returns the daily historical time series for a cryptocurrency
        (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily
        at midnight (UTC). Prices and volumes are quoted in both the market-specific
        currency and USD.

        Args:
            symbol: The cryptocurrency of your choice. It can be any of the "from"
                   currencies in the cryptocurrency list. For example: 'BTC'.
            market: The exchange market of your choice. It can be any of the "to"
                   currencies in the cryptocurrency list. For example: 'EUR'.
            **kwargs: Additional parameters passed to the API.

        Returns:
            Dict containing the daily historical time series data.

        Example:
            >>> # Bitcoin daily data in EUR market
            >>> result = await client.crypto.digital_currency_daily(
            ...     symbol="BTC",
            ...     market="EUR"
            ... )
        """
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            **kwargs,
        }
        return await self.client._make_request(params)

    async def digital_currency_weekly(
        self, symbol: str, market: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Get weekly historical time series for a cryptocurrency traded on a specific market.

        This API returns the weekly historical time series for a cryptocurrency
        (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily
        at midnight (UTC). Prices and volumes are quoted in both the market-specific
        currency and USD.

        Args:
            symbol: The cryptocurrency of your choice. It can be any of the "from"
                   currencies in the cryptocurrency list. For example: 'BTC'.
            market: The exchange market of your choice. It can be any of the "to"
                   currencies in the cryptocurrency list. For example: 'EUR'.
            **kwargs: Additional parameters passed to the API.

        Returns:
            Dict containing the weekly historical time series data.

        Example:
            >>> # Bitcoin weekly data in EUR market
            >>> result = await client.crypto.digital_currency_weekly(
            ...     symbol="BTC",
            ...     market="EUR"
            ... )
        """
        params = {
            "function": "DIGITAL_CURRENCY_WEEKLY",
            "symbol": symbol,
            "market": market,
            **kwargs,
        }
        return await self.client._make_request(params)

    async def digital_currency_monthly(
        self, symbol: str, market: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Get monthly historical time series for a cryptocurrency traded on a specific market.

        This API returns the monthly historical time series for a cryptocurrency
        (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily
        at midnight (UTC). Prices and volumes are quoted in both the market-specific
        currency and USD.

        Args:
            symbol: The cryptocurrency of your choice. It can be any of the "from"
                   currencies in the cryptocurrency list. For example: 'BTC'.
            market: The exchange market of your choice. It can be any of the "to"
                   currencies in the cryptocurrency list. For example: 'EUR'.
            **kwargs: Additional parameters passed to the API.

        Returns:
            Dict containing the monthly historical time series data.

        Example:
            >>> # Bitcoin monthly data in EUR market
            >>> result = await client.crypto.digital_currency_monthly(
            ...     symbol="BTC",
            ...     market="EUR"
            ... )
        """
        params = {
            "function": "DIGITAL_CURRENCY_MONTHLY",
            "symbol": symbol,
            "market": market,
            **kwargs,
        }
        return await self.client._make_request(params)

    # Convenience methods for common use cases
    async def get_bitcoin_price(
        self,
        market: str = "USD",
        period: Literal["daily", "weekly", "monthly"] = "daily",
    ) -> dict[str, Any]:
        """
        Convenience method to get Bitcoin price data.

        Args:
            market: The market currency (default: 'USD').
            period: The time period ('daily', 'weekly', or 'monthly').

        Returns:
            Dict containing Bitcoin price data.
        """
        if period == "daily":
            return await self.digital_currency_daily("BTC", market)
        elif period == "weekly":
            return await self.digital_currency_weekly("BTC", market)
        elif period == "monthly":
            return await self.digital_currency_monthly("BTC", market)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    async def get_ethereum_price(
        self,
        market: str = "USD",
        period: Literal["daily", "weekly", "monthly"] = "daily",
    ) -> dict[str, Any]:
        """
        Convenience method to get Ethereum price data.

        Args:
            market: The market currency (default: 'USD').
            period: The time period ('daily', 'weekly', or 'monthly').

        Returns:
            Dict containing Ethereum price data.
        """
        if period == "daily":
            return await self.digital_currency_daily("ETH", market)
        elif period == "weekly":
            return await self.digital_currency_weekly("ETH", market)
        elif period == "monthly":
            return await self.digital_currency_monthly("ETH", market)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    async def get_crypto_exchange_rates(
        self, crypto_symbols: list[str], target_currency: str = "USD"
    ) -> dict[str, dict[str, Any]]:
        """
        Convenience method to get exchange rates for multiple cryptocurrencies.

        Args:
            crypto_symbols: List of cryptocurrency symbols (e.g., ['BTC', 'ETH', 'LTC']).
            target_currency: The target currency for all exchanges (default: 'USD').

        Returns:
            Dict with cryptocurrency symbols as keys and exchange rate data as values.
        """
        results = {}
        for symbol in crypto_symbols:
            try:
                result = await self.currency_exchange_rate(symbol, target_currency)
                results[symbol] = result
            except Exception as e:
                logger.error(f"Failed to get exchange rate for {symbol}: {e}")
                results[symbol] = {"error": str(e)}

        return results
