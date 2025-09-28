"""
Alpha Vantage API Client
"""

import logging
from datetime import datetime
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """Client for Alpha Vantage API"""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_daily_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Fetch daily time series data from Alpha Vantage"""

        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": self.api_key,
        }

        session = await self._get_session()

        try:
            async with session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                # Check for API errors
                if "Error Message" in data:
                    raise ValueError(
                        f"Alpha Vantage API Error: {data['Error Message']}"
                    )

                if "Note" in data:
                    raise ValueError(f"Alpha Vantage API Limit: {data['Note']}")

                # Parse time series data
                time_series = data.get("Time Series (Daily)", {})

                result = []
                for date_str, values in time_series.items():
                    date = datetime.strptime(date_str, "%Y-%m-%d")

                    # Filter by date range
                    if start_date <= date <= end_date:
                        result.append(
                            {
                                "date": date,
                                "open": float(values["1. open"]),
                                "high": float(values["2. high"]),
                                "low": float(values["3. low"]),
                                "close": float(values["4. close"]),
                                "adjusted_close": float(values["5. adjusted close"]),
                                "volume": int(values["6. volume"]),
                                "dividend_amount": float(values["7. dividend amount"]),
                                "split_coefficient": float(
                                    values["8. split coefficient"]
                                ),
                            }
                        )

                # Sort by date
                result.sort(key=lambda x: x["date"])  # type: ignore[return-value]

                logger.info(f"Fetched {len(result)} records for {symbol}")
                return result

        except aiohttp.ClientError as e:
            logger.error(f"HTTP error fetching data for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise

    async def get_intraday_data(
        self, symbol: str, interval: str = "5min"
    ) -> list[dict[str, Any]]:
        """Fetch intraday time series data from Alpha Vantage"""

        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": "full",
            "apikey": self.api_key,
        }

        session = await self._get_session()

        try:
            async with session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                # Check for API errors
                if "Error Message" in data:
                    raise ValueError(
                        f"Alpha Vantage API Error: {data['Error Message']}"
                    )

                if "Note" in data:
                    raise ValueError(f"Alpha Vantage API Limit: {data['Note']}")

                # Parse time series data
                time_series_key = f"Time Series ({interval})"
                time_series = data.get(time_series_key, {})

                result = []
                for datetime_str, values in time_series.items():
                    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

                    result.append(
                        {
                            "datetime": dt,
                            "open": float(values["1. open"]),
                            "high": float(values["2. high"]),
                            "low": float(values["3. low"]),
                            "close": float(values["4. close"]),
                            "volume": int(values["5. volume"]),
                        }
                    )

                # Sort by datetime
                result.sort(key=lambda x: x["datetime"])  # type: ignore[return-value]

                logger.info(f"Fetched {len(result)} intraday records for {symbol}")
                return result

        except aiohttp.ClientError as e:
            logger.error(f"HTTP error fetching intraday data for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            raise

    async def search_symbol(self, keywords: str) -> list[dict[str, Any]]:
        """Search for symbols using Alpha Vantage symbol search"""

        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key,
        }

        session = await self._get_session()

        try:
            async with session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                # Check for API errors
                if "Error Message" in data:
                    raise ValueError(
                        f"Alpha Vantage API Error: {data['Error Message']}"
                    )

                # Parse search results
                best_matches = data.get("bestMatches", [])

                result = []
                for match in best_matches:
                    result.append(
                        {
                            "symbol": match["1. symbol"],
                            "name": match["2. name"],
                            "type": match["3. type"],
                            "region": match["4. region"],
                            "market_open": match["5. marketOpen"],
                            "market_close": match["6. marketClose"],
                            "timezone": match["7. timezone"],
                            "currency": match["8. currency"],
                            "match_score": float(match["9. matchScore"]),
                        }
                    )

                logger.info(f"Found {len(result)} symbols for '{keywords}'")
                return result

        except aiohttp.ClientError as e:
            logger.error(f"HTTP error searching symbols for '{keywords}': {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching symbols for '{keywords}': {e}")
            raise
