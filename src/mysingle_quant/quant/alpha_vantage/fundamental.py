"""
Alpha Vantage API Client - Fundamental Data Module
"""

import logging
from typing import TYPE_CHECKING, Any, Literal, Optional

from .base import BaseAPIHandler

if TYPE_CHECKING:
    pass  # Remove circular import reference

logger = logging.getLogger(__name__)


class Fundamental(BaseAPIHandler):
    """Fundamental data wrapper for Alpha Vantage API"""

    async def _call_fundamental_api(
        self,
        function: str,
        symbol: Optional[str] = None,
        horizon: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Base method for calling fundamental APIs"""

        # Validate required parameters
        if (
            function not in ["LISTING_STATUS", "EARNINGS_CALENDAR", "IPO_CALENDAR"]
            and not symbol
        ):
            raise ValueError(f"symbol parameter is required for {function}")

        if function == "EARNINGS_ESTIMATES" and not horizon:
            raise ValueError("horizon parameter is required for EARNINGS_ESTIMATES")

        # Build parameters
        params = {
            "function": function,
            "apikey": self.api_key,
        }

        # Add function-specific parameters
        if symbol:
            params["symbol"] = symbol
        if horizon:
            params["horizon"] = horizon

        # Add any additional parameters
        params.update(kwargs)

        data = await self._make_request(params)

        # Parse response based on function type
        return self._parse_fundamental_response(data, function, symbol)

    def _parse_fundamental_response(
        self, data: dict[str, Any], function: str, symbol: Optional[str] = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Parse fundamental API response based on function type"""

        if function == "OVERVIEW":
            return self._parse_overview(data)
        elif function == "ETF_PROFILE":
            return self._parse_etf_profile(data)
        elif function == "DIVIDENDS":
            return self._parse_dividends(data)
        elif function == "SPLITS":
            return self._parse_splits(data)
        elif function == "INCOME_STATEMENT":
            return self._parse_income_statement(data)
        elif function == "BALANCE_SHEET":
            return self._parse_balance_sheet(data)
        elif function == "CASH_FLOW":
            return self._parse_cash_flow(data)
        elif function == "SHARES_OUTSTANDING":
            return self._parse_shares_outstanding(data)
        elif function == "EARNINGS":
            return self._parse_earnings(data)
        elif function == "EARNINGS_ESTIMATES":
            return self._parse_earnings_estimates(data)
        elif function == "LISTING_STATUS":
            return self._parse_listing_status(data)
        elif function == "EARNINGS_CALENDAR":
            return self._parse_earnings_calendar(data)
        elif function == "IPO_CALENDAR":
            return self._parse_ipo_calendar(data)
        else:
            return data  # Return as-is for unknown functions

    def _parse_overview(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse company overview response"""
        return {
            "symbol": data.get("Symbol", ""),
            "asset_type": data.get("AssetType", ""),
            "name": data.get("Name", ""),
            "description": data.get("Description", ""),
            "cik": data.get("CIK", ""),
            "exchange": data.get("Exchange", ""),
            "currency": data.get("Currency", ""),
            "country": data.get("Country", ""),
            "sector": data.get("Sector", ""),
            "industry": data.get("Industry", ""),
            "address": data.get("Address", ""),
            "fiscal_year_end": data.get("FiscalYearEnd", ""),
            "latest_quarter": data.get("LatestQuarter", ""),
            "market_capitalization": self._safe_float(data.get("MarketCapitalization")),
            "ebitda": self._safe_float(data.get("EBITDA")),
            "pe_ratio": self._safe_float(data.get("PERatio")),
            "peg_ratio": self._safe_float(data.get("PEGRatio")),
            "book_value": self._safe_float(data.get("BookValue")),
            "dividend_per_share": self._safe_float(data.get("DividendPerShare")),
            "dividend_yield": self._safe_float(data.get("DividendYield")),
            "eps": self._safe_float(data.get("EPS")),
            "revenue_per_share_ttm": self._safe_float(data.get("RevenuePerShareTTM")),
            "profit_margin": self._safe_float(data.get("ProfitMargin")),
            "operating_margin_ttm": self._safe_float(data.get("OperatingMarginTTM")),
            "return_on_assets_ttm": self._safe_float(data.get("ReturnOnAssetsTTM")),
            "return_on_equity_ttm": self._safe_float(data.get("ReturnOnEquityTTM")),
            "revenue_ttm": self._safe_float(data.get("RevenueTTM")),
            "gross_profit_ttm": self._safe_float(data.get("GrossProfitTTM")),
            "diluted_eps_ttm": self._safe_float(data.get("DilutedEPSTTM")),
            "quarterly_earnings_growth_yoy": self._safe_float(
                data.get("QuarterlyEarningsGrowthYOY")
            ),
            "quarterly_revenue_growth_yoy": self._safe_float(
                data.get("QuarterlyRevenueGrowthYOY")
            ),
            "analyst_target_price": self._safe_float(data.get("AnalystTargetPrice")),
            "trailing_pe": self._safe_float(data.get("TrailingPE")),
            "forward_pe": self._safe_float(data.get("ForwardPE")),
            "price_to_sales_ratio_ttm": self._safe_float(
                data.get("PriceToSalesRatioTTM")
            ),
            "price_to_book_ratio": self._safe_float(data.get("PriceToBookRatio")),
            "ev_to_revenue": self._safe_float(data.get("EVToRevenue")),
            "ev_to_ebitda": self._safe_float(data.get("EVToEBITDA")),
            "beta": self._safe_float(data.get("Beta")),
            "52_week_high": self._safe_float(data.get("52WeekHigh")),
            "52_week_low": self._safe_float(data.get("52WeekLow")),
            "50_day_moving_average": self._safe_float(data.get("50DayMovingAverage")),
            "200_day_moving_average": self._safe_float(data.get("200DayMovingAverage")),
            "shares_outstanding": self._safe_float(data.get("SharesOutstanding")),
            "dividend_date": data.get("DividendDate", ""),
            "ex_dividend_date": data.get("ExDividendDate", ""),
        }

    def _parse_etf_profile(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse ETF profile response"""
        return {
            "symbol": data.get("Symbol", ""),
            "asset_class": data.get("AssetClass", ""),
            "investment_strategy": data.get("InvestmentStrategy", ""),
            "fund_family": data.get("FundFamily", ""),
            "fund_type": data.get("FundType", ""),
            "holdings_count": self._safe_int(data.get("HoldingsCount")),
            "holdings": data.get("Holdings", []),
        }

    def _parse_dividends(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse dividends response"""
        result = []
        for record in data.get("data", []):
            result.append(
                {
                    "symbol": record.get("symbol", ""),
                    "ex_dividend_date": record.get("ex_dividend_date", ""),
                    "dividend_amount": self._safe_float(record.get("dividend_amount")),
                    "declaration_date": record.get("declaration_date", ""),
                    "record_date": record.get("record_date", ""),
                    "payment_date": record.get("payment_date", ""),
                }
            )
        return result

    def _parse_splits(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse stock splits response"""
        result = []
        for record in data.get("data", []):
            result.append(
                {
                    "symbol": record.get("symbol", ""),
                    "split_date": record.get("split_date", ""),
                    "split_coefficient": self._safe_float(
                        record.get("split_coefficient")
                    ),
                }
            )
        return result

    def _parse_income_statement(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse income statement response"""
        return {
            "symbol": data.get("symbol", ""),
            "annual_reports": data.get("annualReports", []),
            "quarterly_reports": data.get("quarterlyReports", []),
        }

    def _parse_balance_sheet(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse balance sheet response"""
        return {
            "symbol": data.get("symbol", ""),
            "annual_reports": data.get("annualReports", []),
            "quarterly_reports": data.get("quarterlyReports", []),
        }

    def _parse_cash_flow(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse cash flow response"""
        return {
            "symbol": data.get("symbol", ""),
            "annual_reports": data.get("annualReports", []),
            "quarterly_reports": data.get("quarterlyReports", []),
        }

    def _parse_shares_outstanding(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse shares outstanding response"""
        result = []
        for record in data.get("data", []):
            result.append(
                {
                    "symbol": record.get("symbol", ""),
                    "date": record.get("date", ""),
                    "shares_outstanding": self._safe_float(
                        record.get("shares_outstanding")
                    ),
                }
            )
        return result

    def _parse_earnings(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse earnings response"""
        return {
            "symbol": data.get("symbol", ""),
            "annual_earnings": data.get("annualEarnings", []),
            "quarterly_earnings": data.get("quarterlyEarnings", []),
        }

    def _parse_earnings_estimates(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse earnings estimates response"""
        return {
            "symbol": data.get("symbol", ""),
            "earnings_estimates": data.get("earningsEstimates", []),
        }

    def _parse_listing_status(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse listing status response"""
        result = []
        for record in data.get("data", []):
            result.append(
                {
                    "symbol": record.get("symbol", ""),
                    "name": record.get("name", ""),
                    "exchange": record.get("exchange", ""),
                    "asset_type": record.get("assetType", ""),
                    "ipo_date": record.get("ipoDate", ""),
                    "delisting_date": record.get("delistingDate", ""),
                    "status": record.get("status", ""),
                }
            )
        return result

    def _parse_earnings_calendar(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse earnings calendar response"""
        result = []
        for record in data.get("data", []):
            result.append(
                {
                    "symbol": record.get("symbol", ""),
                    "name": record.get("name", ""),
                    "report_date": record.get("reportDate", ""),
                    "fiscal_date_ending": record.get("fiscalDateEnding", ""),
                    "estimate": self._safe_float(record.get("estimate")),
                    "currency": record.get("currency", ""),
                }
            )
        return result

    def _parse_ipo_calendar(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse IPO calendar response"""
        result = []
        for record in data.get("data", []):
            result.append(
                {
                    "symbol": record.get("symbol", ""),
                    "name": record.get("name", ""),
                    "ipo_date": record.get("ipoDate", ""),
                    "price_range_low": self._safe_float(record.get("priceRangeLow")),
                    "price_range_high": self._safe_float(record.get("priceRangeHigh")),
                    "currency": record.get("currency", ""),
                    "exchange": record.get("exchange", ""),
                }
            )
        return result

    async def overview(self, symbol: str) -> dict[str, Any]:
        """Get company overview"""
        result = await self._call_fundamental_api("OVERVIEW", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def etf_profile(self, symbol: str) -> dict[str, Any]:
        """Get ETF profile"""
        result = await self._call_fundamental_api("ETF_PROFILE", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def dividends(self, symbol: str) -> list[dict[str, Any]]:
        """Get dividend history"""
        result = await self._call_fundamental_api("DIVIDENDS", symbol=symbol)
        return result if isinstance(result, list) else []

    async def splits(self, symbol: str) -> list[dict[str, Any]]:
        """Get stock split history"""
        result = await self._call_fundamental_api("SPLITS", symbol=symbol)
        return result if isinstance(result, list) else []

    async def income_statement(self, symbol: str) -> dict[str, Any]:
        """Get income statement"""
        result = await self._call_fundamental_api("INCOME_STATEMENT", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def balance_sheet(self, symbol: str) -> dict[str, Any]:
        """Get balance sheet"""
        result = await self._call_fundamental_api("BALANCE_SHEET", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def cash_flow(self, symbol: str) -> dict[str, Any]:
        """Get cash flow statement"""
        result = await self._call_fundamental_api("CASH_FLOW", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def shares_outstanding(self, symbol: str) -> list[dict[str, Any]]:
        """Get shares outstanding"""
        result = await self._call_fundamental_api("SHARES_OUTSTANDING", symbol=symbol)
        return result if isinstance(result, list) else []

    async def earnings(self, symbol: str) -> dict[str, Any]:
        """Get earnings history"""
        result = await self._call_fundamental_api("EARNINGS", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def earnings_estimates(
        self, symbol: str, horizon: Literal["3month", "6month", "12month"]
    ) -> dict[str, Any]:
        """Get earnings estimates"""
        result = await self._call_fundamental_api(
            "EARNINGS_ESTIMATES", symbol=symbol, horizon=horizon
        )
        return result if isinstance(result, dict) else {}

    async def listing_status(self) -> list[dict[str, Any]]:
        """Get listing status"""
        result = await self._call_fundamental_api("LISTING_STATUS")
        return result if isinstance(result, list) else []

    async def earnings_calendar(self) -> list[dict[str, Any]]:
        """Get earnings calendar"""
        result = await self._call_fundamental_api("EARNINGS_CALENDAR")
        return result if isinstance(result, list) else []

    async def ipo_calendar(self) -> list[dict[str, Any]]:
        """Get IPO calendar"""
        result = await self._call_fundamental_api("IPO_CALENDAR")
        return result if isinstance(result, list) else []
