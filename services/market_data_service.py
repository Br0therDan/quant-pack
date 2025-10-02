"""
Market Data Service Layer
"""

import logging
from datetime import UTC, datetime
from typing import Any

import pandas as pd
from app.core.config import get_settings
from app.models.market_data import DataQuality, DataRequest, MarketData
from app.services.database_manager import DatabaseManager

from mysingle_quant import AlphaVantageClient

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for managing market data operations with DuckDB caching"""

    def __init__(self, database_manager: DatabaseManager | None = None):
        self.settings = get_settings()
        self._alpha_vantage = None
        self.database_manager = database_manager

    async def __aenter__(self):
        """Async context manager entry"""
        self._alpha_vantage = AlphaVantageClient(self.settings.ALPHA_VANTAGE_API_KEY)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - clean up resources"""
        if self._alpha_vantage and hasattr(self._alpha_vantage, "close"):
            await self._alpha_vantage.close()

    @property
    def alpha_vantage(self):
        """Get AlphaVantage client - initialize if needed"""
        if self._alpha_vantage is None:
            self._alpha_vantage = AlphaVantageClient(
                self.settings.ALPHA_VANTAGE_API_KEY
            )
        return self._alpha_vantage

    async def close(self):
        """Manually close the service and cleanup resources"""
        if self._alpha_vantage and hasattr(self._alpha_vantage, "close"):
            await self._alpha_vantage.close()
            self._alpha_vantage = None

    async def get_company_overview(self, symbol: str) -> dict[str, Any] | None:
        """Get company overview information"""
        try:
            # Note: This would require mysingle-quant to support company overview API
            # For now, return basic info structure
            logger.info(f"Company overview requested for {symbol}")
            return {
                "Symbol": symbol,
                "Name": f"{symbol} Inc.",
                "Description": f"Company information for {symbol}",
                "Sector": "Unknown",
                "Industry": "Unknown",
                "MarketCapitalization": None,
                "Country": "USA",
                "Currency": "USD",
            }
        except Exception as e:
            logger.error(f"Failed to get company overview for {symbol}: {e}")
            return None

    async def search_symbol(self, keywords: str) -> list[dict[str, Any]]:
        """Search for symbols by keywords"""
        try:
            # Note: This would require mysingle-quant to support symbol search API
            logger.info(f"Symbol search requested for: {keywords}")
            # Return mock results for now
            return [
                {
                    "symbol": keywords.upper(),
                    "name": f"{keywords} Inc.",
                    "type": "Equity",
                    "region": "United States",
                    "marketOpen": "09:30",
                    "marketClose": "16:00",
                    "timezone": "UTC-05",
                    "currency": "USD",
                    "matchScore": 1.0,
                }
            ]
        except Exception as e:
            logger.error(f"Symbol search failed for {keywords}: {e}")
            return []

    async def get_market_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        force_refresh: bool = False,
    ) -> list[MarketData]:
        """Get market data for symbol and date range with DuckDB caching"""

        # First, try DuckDB cache for high-speed access
        if not force_refresh and self.database_manager:
            try:
                start_str = start_date.strftime("%Y-%m-%d")
                end_str = end_date.strftime("%Y-%m-%d")

                cached_df = self.database_manager.get_daily_prices(
                    symbol=symbol, start_date=start_str, end_date=end_str
                )

                if not cached_df.empty and self._is_duckdb_data_complete(
                    cached_df, start_date, end_date
                ):
                    logger.info(f"Returning DuckDB cached data for {symbol}")
                    return self._convert_df_to_market_data_list(cached_df, symbol)

            except Exception as e:
                logger.warning(f"DuckDB cache lookup failed for {symbol}: {e}")

        # Fallback to MongoDB check
        if not force_refresh:
            existing_data = (
                await MarketData.find(
                    MarketData.symbol == symbol,
                    MarketData.date >= start_date,
                    MarketData.date <= end_date,
                )
                .sort("date")
                .to_list()
            )

            if existing_data and self._is_data_complete(
                existing_data, start_date, end_date
            ):
                logger.info(f"Returning MongoDB cached data for {symbol}")
                return existing_data

        # Fetch fresh data from Alpha Vantage
        logger.info(f"Fetching fresh data from Alpha Vantage for {symbol}")
        raw_data = await self.alpha_vantage.get_daily_data(symbol, start_date, end_date)

        if not raw_data:
            logger.warning(f"No data received from Alpha Vantage for {symbol}")
            return []

        # Convert and save to both MongoDB and DuckDB
        market_data_list = []
        df_data = []

        for data_point in raw_data:
            # MongoDB format
            market_data = MarketData(
                symbol=symbol,
                date=data_point["date"],
                open=data_point["open"],
                high=data_point["high"],
                low=data_point["low"],
                close=data_point["close"],
                volume=data_point["volume"],
                adjusted_close=data_point.get("adjusted_close"),
                dividend_amount=data_point.get("dividend_amount"),
                split_coefficient=data_point.get("split_coefficient"),
                source="alpha_vantage",
            )
            market_data_list.append(market_data)

            # DuckDB format
            df_data.append(
                {
                    "symbol": symbol,
                    "open": data_point["open"],
                    "high": data_point["high"],
                    "low": data_point["low"],
                    "close": data_point["close"],
                    "adjusted_close": data_point.get(
                        "adjusted_close", data_point["close"]
                    ),
                    "volume": data_point["volume"],
                    "dividend_amount": data_point.get("dividend_amount", 0.0),
                    "split_coefficient": data_point.get("split_coefficient", 1.0),
                }
            )

        # Save to MongoDB (bulk insert)
        if market_data_list:
            await MarketData.insert_many(market_data_list)
            logger.info(
                f"Saved {len(market_data_list)} records to MongoDB for {symbol}"
            )

        # Save to DuckDB cache for high-speed access
        if df_data and self.database_manager:
            try:
                df = pd.DataFrame(df_data)
                df.index = pd.to_datetime([dp["date"] for dp in raw_data])

                inserted_count = self.database_manager.insert_daily_prices(df)
                logger.info(f"Cached {inserted_count} records in DuckDB for {symbol}")

            except Exception as e:
                logger.error(f"Failed to cache data in DuckDB for {symbol}: {e}")

        return market_data_list

    async def get_intraday_data(
        self, symbol: str, interval: str = "5min", outputsize: str = "compact"
    ) -> list[dict[str, Any]]:
        """Get intraday market data"""
        try:
            logger.info(f"Fetching intraday data for {symbol} with {interval} interval")
            # Note: This would require mysingle-quant to support intraday data
            # For now return empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get intraday data for {symbol}: {e}")
            return []

    async def get_available_symbols(self) -> list[str]:
        """Get list of all available symbols in database"""

        # Use distinct method which is more efficient for this use case
        symbols = await MarketData.distinct("symbol")
        return sorted(symbols) if symbols else []

    async def get_data_coverage(self, symbol: str) -> dict[str, Any]:
        """Get data coverage information for a symbol"""

        # Use simple queries instead of aggregation to avoid cursor issues
        data = await MarketData.find(MarketData.symbol == symbol).to_list()

        if not data:
            return {
                "symbol": symbol,
                "available": False,
                "total_records": 0,
                "date_range": None,
            }

        # Calculate coverage manually
        dates = [d.date for d in data]
        min_date = min(dates)
        max_date = max(dates)
        total_records = len(data)

        result = [
            {
                "_id": symbol,
                "min_date": min_date,
                "max_date": max_date,
                "total_records": total_records,
            }
        ]

        if not result:
            return {
                "symbol": symbol,
                "available": False,
                "total_records": 0,
                "date_range": None,
            }

        data = result[0]
        return {
            "symbol": symbol,
            "available": True,
            "total_records": data["total_records"],
            "date_range": {"start": data["min_date"], "end": data["max_date"]},
        }

    async def analyze_data_quality(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> DataQuality:
        """Analyze data quality for a symbol and date range"""

        # Get market data
        data = (
            await MarketData.find(
                MarketData.symbol == symbol,
                MarketData.date >= start_date,
                MarketData.date <= end_date,
            )
            .sort("date")
            .to_list()
        )

        total_records = len(data)

        # Calculate expected trading days (rough estimate - exclude weekends)
        date_range = (end_date - start_date).days
        expected_trading_days = date_range * 5 // 7  # Rough estimate

        missing_days = max(0, expected_trading_days - total_records)

        # Check for duplicates
        unique_dates = set(d.date.date() for d in data)
        duplicate_records = total_records - len(unique_dates)

        # Check for price anomalies (simple check: price changes > 50% in one day)
        price_anomalies = 0
        for i in range(1, len(data)):
            prev_close = data[i - 1].close_price
            curr_open = data[i].open_price
            if prev_close > 0 and abs(curr_open - prev_close) / prev_close > 0.5:
                price_anomalies += 1

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            total_records,
            missing_days,
            duplicate_records,
            price_anomalies,
            expected_trading_days,
        )

        # Save quality analysis
        quality = DataQuality(
            symbol=symbol,
            date_range_start=start_date,
            date_range_end=end_date,
            total_records=total_records,
            missing_days=missing_days,
            duplicate_records=duplicate_records,
            price_anomalies=price_anomalies,
            quality_score=quality_score,
        )

        await quality.insert()
        return quality

    async def create_data_request(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "daily",
    ) -> DataRequest:
        """Create a data request record"""

        request = DataRequest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        await request.insert()
        return request

    async def update_data_request(
        self,
        request_id: str,
        status: str,
        error_message: str | None = None,
        records_count: int | None = None,
    ):
        """Update data request status"""

        request = await DataRequest.get(request_id)
        if request:
            request.status = status
            if error_message:
                request.error_message = error_message
            if records_count is not None:
                request.records_count = records_count
            if status in ["completed", "failed"]:
                request.completed_at = datetime.now(UTC)

            await request.save()

    def _is_data_complete(
        self, data: list[MarketData], start_date: datetime, end_date: datetime
    ) -> bool:
        """Check if cached data is complete for the date range"""

        if not data:
            return False

        # Check date range coverage
        data_start = min(d.date for d in data)
        data_end = max(d.date for d in data)

        return data_start <= start_date and data_end >= end_date

    def _calculate_quality_score(
        self,
        total_records: int,
        missing_days: int,
        duplicate_records: int,
        price_anomalies: int,
        expected_days: int,
    ) -> float:
        """Calculate data quality score (0-100)"""

        if expected_days == 0:
            return 100.0

        # Base score
        completeness_score = (
            (total_records / expected_days) * 100 if expected_days > 0 else 100
        )
        completeness_score = min(completeness_score, 100)

        # Penalties
        duplicate_penalty = min(duplicate_records * 5, 20)  # Max 20 point penalty
        anomaly_penalty = min(price_anomalies * 3, 15)  # Max 15 point penalty

        quality_score = completeness_score - duplicate_penalty - anomaly_penalty
        return max(quality_score, 0.0)

    def _is_duckdb_data_complete(
        self, df: pd.DataFrame, start_date: datetime, end_date: datetime
    ) -> bool:
        """Check if DuckDB cached data is complete for the date range"""
        if df.empty:
            return False

        # Check date range coverage
        data_start = df.index.min().to_pydatetime()
        data_end = df.index.max().to_pydatetime()

        return data_start <= start_date and data_end >= end_date

    def _convert_df_to_market_data_list(
        self, df: pd.DataFrame, symbol: str
    ) -> list[MarketData]:
        """Convert pandas DataFrame from DuckDB to MarketData list"""
        market_data_list = []

        # Reset index to make 'date' a regular column
        df_reset = df.reset_index()

        for _, row in df_reset.iterrows():
            # Extract date from the index column
            date_value = row["date"] if "date" in row else row.iloc[0]

            # Convert to datetime if it's not already
            if isinstance(date_value, str):
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
            elif hasattr(date_value, "date"):
                date_obj = datetime.combine(date_value.date(), datetime.min.time())
            else:
                # Fallback - assume it's already a datetime
                date_obj = date_value

            market_data = MarketData(
                symbol=symbol,
                date=date_obj,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=int(row["volume"]),
                adjusted_close=float(row.get("adjusted_close", row["close"])),
                dividend_amount=float(row.get("dividend_amount", 0.0)),
                split_coefficient=float(row.get("split_coefficient", 1.0)),
                source="duckdb_cache",
            )
            market_data_list.append(market_data)

        return market_data_list
