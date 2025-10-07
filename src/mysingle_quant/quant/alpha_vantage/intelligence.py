"""
Alpha Vantage API Client - Alpha Intelligence™ Module
Market intelligence and advanced analytics APIs
"""

import logging
from typing import Any, Literal, Optional

from .base import BaseAPIHandler

logger = logging.getLogger(__name__)


class Intelligence(BaseAPIHandler):
    """
    Alpha Intelligence™ APIs
    Advanced market intelligence and analytics
    """

    async def news_sentiment(
        self,
        tickers: Optional[str] = None,
        topics: Optional[str] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        sort: Optional[Literal["LATEST", "EARLIEST", "RELEVANCE"]] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Market News & Sentiment

        Returns live and historical market news & sentiment data from premier news outlets.

        Args:
            tickers: Stock/crypto/forex symbols (e.g., "IBM", "COIN,CRYPTO:BTC,FOREX:USD")
            topics: News topics filter (e.g., "technology", "technology,ipo")
            time_from: Start time in YYYYMMDDTHHMM format (e.g., "20220410T0130")
            time_to: End time in YYYYMMDDTHHMM format
            sort: Sort order for articles
            limit: Number of articles to retrieve (up to 1000)

        Returns:
            Dict containing news articles with sentiment analysis

        Supported topics:
        - blockchain, earnings, ipo, mergers_and_acquisitions
        - financial_markets, economy_fiscal, economy_monetary, economy_macro
        - energy_transportation, finance, life_sciences, manufacturing
        - real_estate, retail_wholesale, technology
        """
        params = {"function": "NEWS_SENTIMENT"}

        if tickers:
            params["tickers"] = tickers
        if topics:
            params["topics"] = topics
        if time_from:
            params["time_from"] = time_from
        if time_to:
            params["time_to"] = time_to
        if sort:
            params["sort"] = sort
        if limit:
            params["limit"] = str(limit)

        return await self.client._make_request(params)

    async def earnings_call_transcript(
        self, symbol: str, quarter: str
    ) -> dict[str, Any]:
        """
        Earnings Call Transcript

        Returns earnings call transcript for a given company in a specific quarter,
        enriched with LLM-based sentiment signals.

        Args:
            symbol: The stock symbol (e.g., "IBM")
            quarter: Fiscal quarter in YYYYQM format (e.g., "2024Q1")

        Returns:
            Dict containing earnings call transcript with sentiment analysis
        """
        params = {
            "function": "EARNINGS_CALL_TRANSCRIPT",
            "symbol": symbol,
            "quarter": quarter,
        }

        return await self.client._make_request(params)

    async def top_gainers_losers(self) -> dict[str, Any]:
        """
        Top Gainers, Losers, and Most Actively Traded Tickers (US Market)

        Returns the top 20 gainers, losers, and most actively traded tickers
        in the US market.

        Returns:
            Dict containing top gainers, losers, and most active tickers
        """
        params = {"function": "TOP_GAINERS_LOSERS"}

        return await self.client._make_request(params)

    async def insider_transactions(self, symbol: str) -> dict[str, Any]:
        """
        Insider Transactions

        Returns the latest and historical insider transactions made by key
        stakeholders (e.g., founders, executives, board members) of a specific company.

        Args:
            symbol: The stock symbol (e.g., "IBM")

        Returns:
            Dict containing insider transaction data
        """
        params = {"function": "INSIDER_TRANSACTIONS", "symbol": symbol}

        return await self.client._make_request(params)

    async def analytics_fixed_window(
        self,
        symbols: str,
        range_param: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "DAILY", "WEEKLY", "MONTHLY"
        ],
        ohlc: Literal["open", "high", "low", "close"],
        calculations: str,
        range_end: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Advanced Analytics (Fixed Window)

        Returns advanced analytics metrics (e.g., total return, variance,
        auto-correlation) for a given time series over a fixed temporal window.

        Args:
            symbols: Comma-separated list of symbols (up to 5 for free, 50 for premium)
            range_param: Date range for the series ("full", "{N}day", "{N}week",
                        "{N}month", "{N}year", or specific date like "2023-07-01")
            interval: Time interval for the data
            ohlc: OHLC price point to use
            calculations: Comma-separated analytics metrics (e.g., "MEAN,STDDEV,CORRELATION")
            range_end: End date for range (optional, for specific date ranges)

        Available calculations:
        - MIN, MAX, MEAN, MEDIAN, CUMULATIVE_RETURN
        - VARIANCE, STDDEV, COVARIANCE, CORRELATION
        - SHARPE_RATIO, AUTO_CORRELATION

        Returns:
            Dict containing calculated analytics metrics
        """
        params = {
            "function": "ANALYTICS_FIXED_WINDOW",
            "SYMBOLS": symbols,
            "RANGE": range_param,
            "INTERVAL": interval,
            "OHLC": ohlc,
            "CALCULATIONS": calculations,
        }

        if range_end:
            params["RANGE_END"] = range_end

        return await self.client._make_request(params)

    async def analytics_sliding_window(
        self,
        symbols: str,
        range_param: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "DAILY", "WEEKLY", "MONTHLY"
        ],
        window_size: int,
        ohlc: Literal["open", "high", "low", "close"],
        calculations: str,
    ) -> dict[str, Any]:
        """
        Advanced Analytics (Sliding Window)

        Returns advanced analytics metrics for a given time series over sliding
        time windows. For example, calculating moving variance over 5 years with
        a window of 100 points to see how variance changes over time.

        Args:
            symbols: Comma-separated list of symbols (up to 5 for free, 50 for premium)
            range_param: Date range for the series ("full", "{N}day", "{N}week",
                        "{N}month", "{N}year")
            interval: Time interval for the data
            window_size: Size of the moving window (minimum 10, recommended larger)
            ohlc: OHLC price point to use
            calculations: Analytics metrics to calculate (1 for free, multiple for premium)

        Available calculations:
        - MEAN, MEDIAN, CUMULATIVE_RETURN
        - VARIANCE, STDDEV, COVARIANCE, CORRELATION
        - SHARPE_RATIO, AUTO_CORRELATION

        Returns:
            Dict containing calculated analytics metrics over time
        """
        params = {
            "function": "ANALYTICS_SLIDING_WINDOW",
            "SYMBOLS": symbols,
            "RANGE": range_param,
            "INTERVAL": interval,
            "WINDOW_SIZE": str(window_size),
            "OHLC": ohlc,
            "CALCULATIONS": calculations,
        }

        return await self.client._make_request(params)

    # Convenience methods for specific analytics
    async def correlation_analysis(
        self,
        symbols: str,
        range_param: str = "1year",
        interval: Literal["DAILY", "WEEKLY", "MONTHLY"] = "DAILY",
    ) -> dict[str, Any]:
        """
        Convenience method for correlation analysis between multiple symbols

        Args:
            symbols: Comma-separated list of symbols (e.g., "AAPL,MSFT,IBM")
            range_param: Date range for analysis
            interval: Time interval for the data

        Returns:
            Dict containing correlation matrix and basic statistics
        """
        return await self.analytics_fixed_window(
            symbols=symbols,
            range_param=range_param,
            interval=interval,
            ohlc="close",
            calculations="MEAN,STDDEV,CORRELATION",
        )

    async def risk_metrics(
        self,
        symbol: str,
        range_param: str = "1year",
        interval: Literal["DAILY", "WEEKLY", "MONTHLY"] = "DAILY",
    ) -> dict[str, Any]:
        """
        Convenience method for risk analysis of a single symbol

        Args:
            symbol: Stock symbol to analyze
            range_param: Date range for analysis
            interval: Time interval for the data

        Returns:
            Dict containing risk metrics (variance, standard deviation, etc.)
        """
        return await self.analytics_fixed_window(
            symbols=symbol,
            range_param=range_param,
            interval=interval,
            ohlc="close",
            calculations="MEAN,VARIANCE,STDDEV,CUMULATIVE_RETURN,SHARPE_RATIO",
        )

    async def rolling_volatility(
        self,
        symbol: str,
        window_size: int = 20,
        range_param: str = "3month",
        interval: Literal["DAILY", "WEEKLY"] = "DAILY",
    ) -> dict[str, Any]:
        """
        Convenience method for rolling volatility analysis

        Args:
            symbol: Stock symbol to analyze
            window_size: Size of the rolling window
            range_param: Date range for analysis
            interval: Time interval for the data

        Returns:
            Dict containing rolling volatility metrics
        """
        return await self.analytics_sliding_window(
            symbols=symbol,
            range_param=range_param,
            interval=interval,
            window_size=window_size,
            ohlc="close",
            calculations="STDDEV",
        )
