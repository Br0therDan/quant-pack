"""
Alpha Vantage Options Data APIs
- Documentation: https://www.alphavantage.co/documentation/#options
"""

from typing import Any, Literal, Optional

from .base import BaseAPIHandler


class Options(BaseAPIHandler):
    """
    Options Data API handler for Alpha Vantage

    This suite of APIs provide realtime and historical US options data,
    spanning 15+ years of history with full market/volume coverage.
    """

    async def realtime_options(
        self,
        symbol: str,
        require_greeks: Optional[bool] = None,
        contract: Optional[str] = None,
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get realtime US options data with full market coverage.

        This API returns realtime US options data with full market coverage.
        Option chains are sorted by expiration dates in chronological order.
        Within the same expiration date, contracts are sorted by strike prices from low to high.

        Args:
            symbol: The name of the equity (e.g., "IBM")
            require_greeks: Enable greeks & implied volatility (IV) fields.
                          By default, require_greeks=false. Set require_greeks=true
                          to enable greeks & IVs in the API response
            contract: The US options contract ID. By default, the contract parameter
                     is not set and the entire option chain for a given symbol will be returned
            datatype: Output format ("json" or "csv")

        Returns:
            Dictionary containing realtime options data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.options.realtime_options("IBM")
            >>> print(data)
        """
        params = {"function": "REALTIME_OPTIONS", "symbol": symbol}

        if require_greeks is not None:
            params["require_greeks"] = str(require_greeks).lower()
        if contract is not None:
            params["contract"] = contract
        if datatype != "json":
            params["datatype"] = datatype

        return await self.client._make_request(params)

    async def historical_options(
        self,
        symbol: str,
        date: Optional[str] = None,
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get historical options chain for a specific symbol on a specific date.

        This API returns the full historical options chain for a specific symbol
        on a specific date, covering 15+ years of history. Implied volatility (IV)
        and common Greeks (e.g., delta, gamma, theta, vega, rho) are also returned.
        Option chains are sorted by expiration dates in chronological order.
        Within the same expiration date, contracts are sorted by strike prices from low to high.

        Args:
            symbol: The name of the equity (e.g., "IBM")
            date: Date in YYYY-MM-DD format. By default, the date parameter is not set
                 and the API will return data for the previous trading session.
                 Any date later than 2008-01-01 is accepted (e.g., "2017-11-15")
            datatype: Output format ("json" or "csv")

        Returns:
            Dictionary containing historical options data

        Example:
            >>> client = AlphaVantageClient("your_api_key")
            >>> data = await client.options.historical_options("IBM", "2017-11-15")
            >>> print(data)
        """
        params = {"function": "HISTORICAL_OPTIONS", "symbol": symbol}

        if date is not None:
            params["date"] = date
        if datatype != "json":
            params["datatype"] = datatype

        return await self.client._make_request(params)

    # Convenience methods for common use cases
    async def get_option_chain(
        self, symbol: str, with_greeks: bool = True
    ) -> dict[str, Any]:
        """
        Get complete realtime option chain with Greeks and implied volatility.

        Convenience method to get the full option chain for a symbol with
        Greeks and implied volatility data included.

        Args:
            symbol: The equity symbol
            with_greeks: Whether to include Greeks and IV data

        Returns:
            Dictionary containing complete option chain data
        """
        return await self.realtime_options(symbol=symbol, require_greeks=with_greeks)

    async def get_historical_chain(self, symbol: str, date: str) -> dict[str, Any]:
        """
        Get historical option chain for a specific date.

        Convenience method to get historical options data for a specific trading date.

        Args:
            symbol: The equity symbol
            date: Date in YYYY-MM-DD format

        Returns:
            Dictionary containing historical option chain data
        """
        return await self.historical_options(symbol=symbol, date=date)

    async def get_option_contract(
        self, symbol: str, contract_id: str, with_greeks: bool = True
    ) -> dict[str, Any]:
        """
        Get specific option contract data.

        Convenience method to get data for a specific option contract
        instead of the entire option chain.

        Args:
            symbol: The equity symbol
            contract_id: The US options contract ID (e.g., "IBM270115C00390000")
            with_greeks: Whether to include Greeks and IV data

        Returns:
            Dictionary containing specific option contract data
        """
        return await self.realtime_options(
            symbol=symbol, contract=contract_id, require_greeks=with_greeks
        )
