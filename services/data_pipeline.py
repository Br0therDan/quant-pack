"""
Data Pipeline Service
Port of the original data_service pipeline functionality
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings
from app.models.company import Company, Watchlist
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


class DataPipeline:
    """Data collection and processing pipeline"""

    def __init__(self):
        self.settings = get_settings()
        self.market_service = MarketDataService()
        self.symbols_to_update: list[str] = []

    async def setup_default_symbols(self) -> None:
        """Setup default watchlist symbols"""
        # Try to load from database first
        try:
            watchlist = await Watchlist.find_one(Watchlist.name == "default")
            if watchlist and watchlist.symbols:
                self.symbols_to_update = watchlist.symbols
                logger.info(
                    f"Loaded {len(watchlist.symbols)} symbols from database watchlist"
                )
                return
        except Exception as e:
            logger.warning(f"Failed to load watchlist from database: {e}")

        # Fall back to hardcoded defaults
        default_symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "JPM",
            "JNJ",
            "V",
        ]

        logger.info(f"Setting up default symbols: {default_symbols}")
        self.symbols_to_update = default_symbols

        # Save to database for future use
        await self._update_default_watchlist(default_symbols)

    async def update_watchlist(self, symbols: list[str]) -> None:
        """Update the watchlist with new symbols"""
        self.symbols_to_update = symbols
        logger.info(f"Watchlist updated with {len(symbols)} symbols")

        # Update or create default watchlist in database
        await self._update_default_watchlist(symbols)

    async def _update_default_watchlist(self, symbols: list[str]) -> None:
        """Update the default watchlist in database"""
        try:
            watchlist = await Watchlist.find_one(Watchlist.name == "default")

            if watchlist:
                watchlist.symbols = symbols
                watchlist.updated_at = datetime.now(UTC)
                await watchlist.save()
            else:
                watchlist = Watchlist(
                    name="default",
                    description="Default pipeline watchlist",
                    symbols=symbols,
                    auto_update=True,
                    update_interval=3600,
                    last_updated=datetime.now(UTC),
                )
                await watchlist.insert()

            logger.debug("Default watchlist updated in database")
        except Exception as e:
            logger.error(f"Failed to update default watchlist: {e}")

    async def collect_stock_info(self, symbol: str) -> bool:
        """Collect basic stock information"""
        try:
            info = await self.market_service.get_company_overview(symbol)
            if info:
                # Store company information in a separate collection
                await self._store_company_info(symbol, info)
                logger.info(f"Stock info collected for {symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to collect stock info for {symbol}: {e}")
            return False

    async def _store_company_info(self, symbol: str, info: dict[str, Any]) -> None:
        """Store company information in the database"""
        try:
            # Check if company already exists
            existing_company = await Company.find_one(Company.symbol == symbol)

            company_data = {
                "symbol": symbol,
                "name": info.get("Name", f"{symbol} Inc."),
                "description": info.get("Description"),
                "sector": info.get("Sector"),
                "industry": info.get("Industry"),
                "country": info.get("Country"),
                "currency": info.get("Currency"),
                "exchange": info.get("Exchange"),
                "market_cap": self._parse_market_cap(info.get("MarketCapitalization")),
                "shares_outstanding": self._parse_int(info.get("SharesOutstanding")),
                "pe_ratio": self._parse_float(info.get("PERatio")),
                "dividend_yield": self._parse_float(info.get("DividendYield")),
                "updated_at": datetime.now(UTC),
            }

            if existing_company:
                # Update existing company
                for key, value in company_data.items():
                    if value is not None:
                        setattr(existing_company, key, value)
                await existing_company.save()
                logger.debug(f"Updated company info for {symbol}")
            else:
                # Create new company record
                company_data["created_at"] = datetime.now(UTC)
                company = Company(**company_data)
                await company.insert()
                logger.debug(f"Created new company record for {symbol}")

        except Exception as e:
            logger.error(f"Failed to store company info for {symbol}: {e}")

    def _parse_market_cap(self, value: Any) -> int | None:
        """Parse market capitalization value"""
        if not value:
            return None
        try:
            if isinstance(value, str):
                # Remove common suffixes and convert
                value = value.replace(",", "").replace("$", "")
                if "B" in value.upper():
                    return int(
                        float(value.replace("B", "").replace("b", "")) * 1_000_000_000
                    )
                elif "M" in value.upper():
                    return int(
                        float(value.replace("M", "").replace("m", "")) * 1_000_000
                    )
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _parse_float(self, value: Any) -> float | None:
        """Parse float value safely"""
        if not value or value == "None":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value: Any) -> int | None:
        """Parse integer value safely"""
        if not value or value == "None":
            return None
        try:
            return int(float(str(value).replace(",", "")))
        except (ValueError, TypeError):
            return None

    async def collect_daily_data(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> bool:
        """Collect daily price data for a symbol"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=100)
            if not end_date:
                end_date = datetime.now()

            data = await self.market_service.get_market_data(
                symbol, start_date, end_date, force_refresh=True
            )

            if data:
                logger.info(f"Daily data collected for {symbol}: {len(data)} records")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to collect daily data for {symbol}: {e}")
            return False

    async def run_full_update(self, symbols: list[str] | None = None) -> dict[str, Any]:
        """Run full data update for specified symbols"""
        target_symbols = symbols or self.symbols_to_update

        if not target_symbols:
            await self.setup_default_symbols()
            target_symbols = self.symbols_to_update

        results = {
            "total_symbols": len(target_symbols),
            "successful_updates": 0,
            "failed_updates": 0,
            "details": [],
        }

        logger.info(f"Starting full update for {len(target_symbols)} symbols")

        for symbol in target_symbols:
            try:
                # Collect basic info
                info_success = await self.collect_stock_info(symbol)

                # Collect daily data
                data_success = await self.collect_daily_data(symbol)

                if info_success and data_success:
                    results["successful_updates"] += 1
                    results["details"].append(
                        {
                            "symbol": symbol,
                            "status": "success",
                            "info_collected": info_success,
                            "data_collected": data_success,
                        }
                    )
                else:
                    results["failed_updates"] += 1
                    results["details"].append(
                        {
                            "symbol": symbol,
                            "status": "failed",
                            "info_collected": info_success,
                            "data_collected": data_success,
                        }
                    )

                # Small delay to respect rate limits
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Update failed for {symbol}: {e}")
                results["failed_updates"] += 1
                results["details"].append(
                    {"symbol": symbol, "status": "error", "error": str(e)}
                )

        logger.info(
            f"Full update completed: {results['successful_updates']} successful, {results['failed_updates']} failed"
        )
        return results

    async def get_update_status(self) -> dict[str, Any]:
        """Get current update status and statistics"""
        try:
            total_symbols = len(self.symbols_to_update)

            # Get data coverage for watchlist symbols
            coverage_info = []
            for symbol in self.symbols_to_update:
                coverage = await self._get_symbol_coverage(symbol)
                coverage_info.append(coverage)

            return {
                "watchlist_size": total_symbols,
                "symbols": self.symbols_to_update,
                "coverage": coverage_info,
                "last_check": datetime.now(UTC),
            }

        except Exception as e:
            logger.error(f"Failed to get update status: {e}")
            return {"error": str(e)}

    async def _get_symbol_coverage(self, symbol: str) -> dict[str, Any]:
        """Get data coverage information for a symbol"""
        try:
            # Check if company info exists
            company = await Company.find_one(Company.symbol == symbol)
            company_info_exists = company is not None

            # Get market data coverage - this would ideally check the actual data
            # For now, provide basic coverage info
            coverage = {
                "symbol": symbol,
                "company_info": company_info_exists,
                "market_data": False,  # Would need to check MarketData collection
                "last_update": company.updated_at if company else None,
                "data_points": 0,  # Would count actual data points
            }

            return coverage
        except Exception as e:
            logger.error(f"Failed to get coverage for {symbol}: {e}")
            return {
                "symbol": symbol,
                "company_info": False,
                "market_data": False,
                "error": str(e),
            }

    async def get_company_info(self, symbol: str) -> Company | None:
        """Get stored company information"""
        try:
            return await Company.find_one(Company.symbol == symbol)
        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {e}")
            return None

    async def get_all_companies(self) -> list[Company]:
        """Get all stored companies"""
        try:
            return await Company.find_all().to_list()
        except Exception as e:
            logger.error(f"Failed to get all companies: {e}")
            return []

    async def create_watchlist(
        self, name: str, symbols: list[str], description: str = ""
    ) -> Watchlist | None:
        """Create a new watchlist"""
        try:
            watchlist = Watchlist(
                name=name,
                description=description,
                symbols=symbols,
                auto_update=True,
                update_interval=3600,
                last_updated=datetime.now(UTC),
            )
            await watchlist.insert()
            logger.info(f"Created watchlist '{name}' with {len(symbols)} symbols")
            return watchlist
        except Exception as e:
            logger.error(f"Failed to create watchlist '{name}': {e}")
            return None

    async def get_watchlist(self, name: str) -> Watchlist | None:
        """Get a watchlist by name"""
        try:
            return await Watchlist.find_one(Watchlist.name == name)
        except Exception as e:
            logger.error(f"Failed to get watchlist '{name}': {e}")
            return None

    async def list_watchlists(self) -> list[Watchlist]:
        """List all watchlists"""
        try:
            return await Watchlist.find_all().to_list()
        except Exception as e:
            logger.error(f"Failed to list watchlists: {e}")
            return []

    async def cleanup(self) -> None:
        """Cleanup pipeline resources"""
        await self.market_service.close()
