"""
Alpha Vantage API Client - Economic Indicators Module

This module provides access to Alpha Vantage's Economic Indicators APIs,
which provide key US economic indicators frequently used for investment
strategy formulation and application development.

Economic Indicators APIs:
- REAL_GDP: Real Gross Domestic Product
- REAL_GDP_PER_CAPITA: Real GDP per Capita
- TREASURY_YIELD: Treasury Yield
- FEDERAL_FUNDS_RATE: Federal Funds Rate
- CPI: Consumer Price Index
- INFLATION: Inflation
- RETAIL_SALES: Retail Sales
- DURABLES: Durable Goods Orders
- UNEMPLOYMENT: Unemployment Rate
- NONFARM_PAYROLL: Nonfarm Payrolls
"""

from typing import Any, Literal

from .base import BaseAPIHandler


class EconomicIndicators(BaseAPIHandler):
    """
    Economic Indicators API handler for Alpha Vantage.

    This class provides methods to access key US economic indicators
    that are frequently used for investment strategy formulation
    and application development.
    """

    async def real_gdp(
        self,
        interval: Literal["quarterly", "annual"] = "annual",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get the annual and quarterly Real GDP of the United States.

        This API returns the Real Gross Domestic Product data, which represents
        the annual and quarterly economic output adjusted for inflation.

        Args:
            interval: Data frequency. Options: "quarterly", "annual"
            datatype: Response format. Options: "json", "csv"

        Returns:
            Real GDP time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.real_gdp()
            >>> data = await client.economic_indicators.real_gdp(interval="quarterly")
        """
        params = {"function": "REAL_GDP", "interval": interval, "datatype": datatype}
        return await self.client._make_request(params)

    async def real_gdp_per_capita(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the quarterly Real GDP per Capita data of the United States.

        This API returns the Real GDP per capita, which represents the
        economic output per person adjusted for inflation.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Real GDP per capita time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.real_gdp_per_capita()
        """
        params = {"function": "REAL_GDP_PER_CAPITA", "datatype": datatype}
        return await self.client._make_request(params)

    async def treasury_yield(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
        maturity: Literal[
            "3month", "2year", "5year", "7year", "10year", "30year"
        ] = "10year",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get the US treasury yield of a given maturity timeline.

        This API returns the daily, weekly, and monthly US treasury yield
        for various maturity periods (3-month to 30-year).

        Args:
            interval: Data frequency. Options: "daily", "weekly", "monthly"
            maturity: Treasury maturity period. Options: "3month", "2year", "5year", "7year", "10year", "30year"
            datatype: Response format. Options: "json", "csv"

        Returns:
            Treasury yield time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.treasury_yield()
            >>> data = await client.economic_indicators.treasury_yield(maturity="2year", interval="weekly")
        """
        params = {
            "function": "TREASURY_YIELD",
            "interval": interval,
            "maturity": maturity,
            "datatype": datatype,
        }
        return await self.client._make_request(params)

    async def federal_funds_rate(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get the daily, weekly, and monthly federal funds rate (interest rate) of the United States.

        This API returns the federal funds effective rate, which is the interest rate
        at which depository institutions trade federal funds with each other overnight.

        Args:
            interval: Data frequency. Options: "daily", "weekly", "monthly"
            datatype: Response format. Options: "json", "csv"

        Returns:
            Federal funds rate time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.federal_funds_rate()
            >>> data = await client.economic_indicators.federal_funds_rate(interval="weekly")
        """
        params = {
            "function": "FEDERAL_FUNDS_RATE",
            "interval": interval,
            "datatype": datatype,
        }
        return await self.client._make_request(params)

    async def cpi(
        self,
        interval: Literal["monthly", "semiannual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        Get the monthly and semiannual consumer price index (CPI) of the United States.

        CPI is widely regarded as the barometer of inflation levels in the broader economy.
        This API returns the Consumer Price Index for All Urban Consumers.

        Args:
            interval: Data frequency. Options: "monthly", "semiannual"
            datatype: Response format. Options: "json", "csv"

        Returns:
            CPI time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.cpi()
            >>> data = await client.economic_indicators.cpi(interval="semiannual")
        """
        params = {"function": "CPI", "interval": interval, "datatype": datatype}
        return await self.client._make_request(params)

    async def inflation(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the annual inflation rates (consumer prices) of the United States.

        This API returns the annual inflation rates based on consumer prices,
        which measures the rate of increase in prices over time.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Inflation time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.inflation()
        """
        params = {"function": "INFLATION", "datatype": datatype}
        return await self.client._make_request(params)

    async def retail_sales(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the monthly Advance Retail Sales: Retail Trade data of the United States.

        This API returns retail trade data, which measures the total receipts
        of retail stores and provides insights into consumer spending patterns.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Retail sales time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.retail_sales()
        """
        params = {"function": "RETAIL_SALES", "datatype": datatype}
        return await self.client._make_request(params)

    async def durables(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the monthly manufacturers' new orders of durable goods in the United States.

        Durable goods are products that are expected to last for at least three years.
        This indicator provides insights into manufacturing activity and business investment.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Durable goods orders time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.durables()
        """
        params = {"function": "DURABLES", "datatype": datatype}
        return await self.client._make_request(params)

    async def unemployment(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the monthly unemployment data of the United States.

        The unemployment rate represents the number of unemployed as a percentage
        of the labor force. This is a key indicator of economic health.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Unemployment rate time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.unemployment()
        """
        params = {"function": "UNEMPLOYMENT", "datatype": datatype}
        return await self.client._make_request(params)

    async def nonfarm_payroll(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the monthly US All Employees: Total Nonfarm (commonly known as Total Nonfarm Payroll).

        This measures the number of U.S. workers in the economy that excludes proprietors,
        private household employees, unpaid volunteers, farm employees, and
        the unincorporated self-employed.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Nonfarm payroll time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.nonfarm_payroll()
        """
        params = {"function": "NONFARM_PAYROLL", "datatype": datatype}
        return await self.client._make_request(params)

    # Convenience methods for common use cases
    async def get_key_indicators(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get a collection of key economic indicators in a single call.

        This convenience method fetches multiple key economic indicators:
        - Real GDP (annual)
        - Treasury Yield (10-year, monthly)
        - Federal Funds Rate (monthly)
        - CPI (monthly)
        - Unemployment Rate

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Dictionary containing multiple economic indicators

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> indicators = await client.economic_indicators.get_key_indicators()
        """
        import asyncio

        # Fetch multiple indicators concurrently
        tasks = [
            self.real_gdp(datatype=datatype),
            self.treasury_yield(datatype=datatype),
            self.federal_funds_rate(datatype=datatype),
            self.cpi(datatype=datatype),
            self.unemployment(datatype=datatype),
        ]

        results = await asyncio.gather(*tasks)

        return {
            "real_gdp": results[0],
            "treasury_yield_10y": results[1],
            "federal_funds_rate": results[2],
            "cpi": results[3],
            "unemployment": results[4],
        }

    async def get_monetary_policy_indicators(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get monetary policy related indicators.

        This convenience method fetches indicators related to monetary policy:
        - Federal Funds Rate
        - Treasury Yield (10-year)
        - Inflation

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Dictionary containing monetary policy indicators

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> indicators = await client.economic_indicators.get_monetary_policy_indicators()
        """
        import asyncio

        tasks = [
            self.federal_funds_rate(datatype=datatype),
            self.treasury_yield(datatype=datatype),
            self.inflation(datatype=datatype),
        ]

        results = await asyncio.gather(*tasks)

        return {
            "federal_funds_rate": results[0],
            "treasury_yield_10y": results[1],
            "inflation": results[2],
        }

    async def get_economic_growth_indicators(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get economic growth related indicators.

        This convenience method fetches indicators related to economic growth:
        - Real GDP (annual)
        - Real GDP per Capita
        - Retail Sales
        - Durable Goods Orders
        - Nonfarm Payroll

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Dictionary containing economic growth indicators

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> indicators = await client.economic_indicators.get_economic_growth_indicators()
        """
        import asyncio

        tasks = [
            self.real_gdp(datatype=datatype),
            self.real_gdp_per_capita(datatype=datatype),
            self.retail_sales(datatype=datatype),
            self.durables(datatype=datatype),
            self.nonfarm_payroll(datatype=datatype),
        ]

        results = await asyncio.gather(*tasks)

        return {
            "real_gdp": results[0],
            "real_gdp_per_capita": results[1],
            "retail_sales": results[2],
            "durable_goods": results[3],
            "nonfarm_payroll": results[4],
        }
