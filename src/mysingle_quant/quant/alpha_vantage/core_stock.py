"""
Alpha Vantage API 클라이언트 - 코어 주식 모듈

주식 데이터 API에 대한 접근을 제공합니다.
시계열 데이터, 실시간 주가, 심볼 검색 등의 기능을 지원합니다.

지원하는 기능:
- 인트라데이 시계열 데이터
- 일별/주별/월별 시계열 데이터
- 주가 조정 데이터
- 실시간 주가 조회
- 심볼 검색
- 시장 상태 확인
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional

from .base import BaseAPIHandler

if TYPE_CHECKING:
    pass  # Remove circular import reference

logger = logging.getLogger(__name__)


class CoreStock(BaseAPIHandler):
    """
    코어 주식 데이터 API 핸들러

    Alpha Vantage의 코어 주식 데이터 API에 대한 인터페이스를 제공합니다.
    다양한 시간 간격과 데이터 형식을 지원하며,
    20+ 년의 역사적 데이터를 제공합니다.

    지원하는 API 기능:
    - TIME_SERIES_INTRADAY: 인트라데이 데이터 (1분~60분)
    - TIME_SERIES_DAILY: 일별 데이터
    - TIME_SERIES_WEEKLY: 주별 데이터
    - TIME_SERIES_MONTHLY: 월별 데이터
    - GLOBAL_QUOTE: 실시간 주가
    - SYMBOL_SEARCH: 심볼 검색
    - MARKET_STATUS: 시장 상태

    사용 예제:
        >>> client = AlphaVantageClient()
        >>> # 일별 데이터 조회
        >>> daily_data = await client.stock.time_series_daily("AAPL")
        >>> # 실시간 주가 조회
        >>> quote = await client.stock.global_quote("AAPL")
    """

    async def _call_core_stock_api(
        self,
        function: str,
        symbol: Optional[str] = None,
        keywords: Optional[str] = None,
        interval: Optional[str] = None,
        adjusted: Optional[bool] = None,
        extended_hours: Optional[bool] = None,
        outputsize: Optional[str] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        코어 주식 API 호출을 위한 기본 메서드

        Args:
            function: API 함수 이름
            symbol: 주식 심볼 (e.g., "AAPL")
            keywords: 심볼 검색 키워드 (SYMBOL_SEARCH용)
            interval: 시간 간격 (INTRADAY용)
            adjusted: 주가 조정 여부
            extended_hours: 연장 거래 시간 포함 여부
            outputsize: 출력 크기 ("compact" 또는 "full")
            start_date: 시작 날짜
            end_date: 종료 날짜
            **kwargs: 추가 파라미터

        Returns:
            API 응답 데이터 (리스트 또는 딕셔너리)

        Raises:
            ValueError: 필수 파라미터가 빠진 경우
        """

        # Validate required parameters
        if function == "SYMBOL_SEARCH" and not keywords:
            raise ValueError("keywords parameter is required for SYMBOL_SEARCH")

        if function == "TIME_SERIES_INTRADAY" and not interval:
            raise ValueError("interval parameter is required for TIME_SERIES_INTRADAY")

        if function not in ["SYMBOL_SEARCH", "MARKET_STATUS"] and not symbol:
            raise ValueError(f"symbol parameter is required for {function}")

        # Build parameters
        params = {
            "function": function,
            "apikey": self.api_key,
        }

        # Add function-specific parameters
        if symbol:
            params["symbol"] = symbol
        if keywords:
            params["keywords"] = keywords
        if interval:
            params["interval"] = interval
        if adjusted is not None:
            params["adjusted"] = "true" if adjusted else "false"
        if extended_hours is not None:
            params["extended_hours"] = "true" if extended_hours else "false"
        if outputsize:
            params["outputsize"] = outputsize

        # Add any additional parameters
        params.update(kwargs)

        data = await self._make_request(params)

        # Parse response based on function type
        return self._parse_core_stock_response(
            data, function, symbol, interval, start_date, end_date
        )

    def _parse_core_stock_response(
        self,
        data: dict[str, Any],
        function: str,
        symbol: Optional[str] = None,
        interval: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        API 응답을 함수 타입에 따라 파싱합니다

        Args:
            data: API 원시 응답 데이터
            function: API 함수 이름
            symbol: 주식 심볼
            interval: 시간 간격
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            파싱된 데이터 (리스트 또는 딕셔너리)
        """

        if function == "SYMBOL_SEARCH":
            return self._parse_symbol_search(data)
        elif function == "GLOBAL_QUOTE":
            return self._parse_global_quote(data)
        elif function == "MARKET_STATUS":
            return data  # Return as-is for market status
        elif function == "REALTIME_BULK_QUOTES":
            return data  # Return as-is for bulk quotes
        elif function.startswith("TIME_SERIES"):
            return self._parse_time_series(
                data, function, interval, start_date, end_date
            )
        else:
            return data  # Return as-is for unknown functions

    def _parse_symbol_search(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        심볼 검색 응답을 파싱합니다

        Args:
            data: API 원시 응답 데이터

        Returns:
            검색 결과 리스트 (심볼, 이름, 타입 등 정보 포함)
        """
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
        return result

    def _parse_global_quote(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        글로벌 주가 응답을 파싱합니다

        Args:
            data: API 원시 응답 데이터

        Returns:
            주가 정보 (시가, 고가, 저가, 종가, 거래량 등)
        """
        quote = data.get("Global Quote", {})
        if not quote:
            return {}
        return {
            "symbol": quote.get("01. symbol", ""),
            "open": self._safe_float(quote.get("02. open", 0)),
            "high": self._safe_float(quote.get("03. high", 0)),
            "low": self._safe_float(quote.get("04. low", 0)),
            "price": self._safe_float(quote.get("05. price", 0)),
            "volume": self._safe_int(quote.get("06. volume", 0)),
            "latest_trading_day": quote.get("07. latest trading day", ""),
            "previous_close": self._safe_float(quote.get("08. previous close", 0)),
            "change": self._safe_float(quote.get("09. change", 0)),
            "change_percent": quote.get("10. change percent", ""),
        }

    def _parse_time_series(
        self,
        data: dict[str, Any],
        function: str,
        interval: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        시계열 데이터 응답을 파싱합니다

        Args:
            data: API 원시 응답 데이터
            function: API 함수 이름
            interval: 시간 간격
            start_date: 시작 날짜 (필터링용)
            end_date: 종료 날짜 (필터링용)

        Returns:
            시계열 데이터 리스트 (날짜, OHLCV 데이터 포함)
        """

        # Determine the time series key
        if function == "TIME_SERIES_INTRADAY" and interval:
            time_series_key = f"Time Series ({interval})"
            datetime_format = "%Y-%m-%d %H:%M:%S"
            datetime_field = "datetime"
        elif (
            function == "TIME_SERIES_DAILY" or function == "TIME_SERIES_DAILY_ADJUSTED"
        ):
            time_series_key = "Time Series (Daily)"
            datetime_format = "%Y-%m-%d"
            datetime_field = "date"
        elif function == "TIME_SERIES_WEEKLY":
            time_series_key = "Weekly Time Series"
            datetime_format = "%Y-%m-%d"
            datetime_field = "date"
        elif function == "TIME_SERIES_WEEKLY_ADJUSTED":
            time_series_key = "Weekly Adjusted Time Series"
            datetime_format = "%Y-%m-%d"
            datetime_field = "date"
        elif function == "TIME_SERIES_MONTHLY":
            time_series_key = "Monthly Time Series"
            datetime_format = "%Y-%m-%d"
            datetime_field = "date"
        elif function == "TIME_SERIES_MONTHLY_ADJUSTED":
            time_series_key = "Monthly Adjusted Time Series"
            datetime_format = "%Y-%m-%d"
            datetime_field = "date"
        else:
            return []

        time_series = data.get(time_series_key, {})
        result = []

        for date_str, values in time_series.items():
            dt = datetime.strptime(date_str, datetime_format)

            # Filter by date range if provided
            if start_date and dt < start_date:
                continue
            if end_date and dt > end_date:
                continue

            # Base data structure
            record = {
                datetime_field: dt,
                "open": self._safe_float(values["1. open"]),
                "high": self._safe_float(values["2. high"]),
                "low": self._safe_float(values["3. low"]),
                "close": self._safe_float(values["4. close"]),
                "volume": self._safe_int(values.get("5. volume", 0)),
            }

            # Add adjusted data if available
            if "adjusted" in function.lower():
                if "5. adjusted close" in values:
                    record["adjusted_close"] = self._safe_float(
                        values["5. adjusted close"]
                    )
                if "6. volume" in values:
                    record["volume"] = self._safe_int(values["6. volume"])
                if "7. dividend amount" in values:
                    record["dividend_amount"] = self._safe_float(
                        values["7. dividend amount"]
                    )
                if "8. split coefficient" in values:
                    record["split_coefficient"] = self._safe_float(
                        values["8. split coefficient"]
                    )

            result.append(record)

        # Sort by datetime
        result.sort(key=lambda x: x[datetime_field])

        logger.info(f"Parsed {len(result)} records for {function}")
        return result

    async def intraday(
        self,
        symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"],
        adjusted: Optional[bool] = None,
        extended_hours: Optional[bool] = None,
        outputsize: Optional[Literal["compact", "full"]] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        인트라데이 시계열 데이터를 가져옵니다

        현재 및 20+ 년의 역사적 인트라데이 OHLCV 시계열 데이터를 반환합니다.
        프리마켓 및 포스트마켓 시간대를 포함합니다.

        Args:
            symbol: 주식 심볼 (e.g., "AAPL")
            interval: 시간 간격 (1min, 5min, 15min, 30min, 60min)
            adjusted: 주가 조정 여부 (기본값: True)
            extended_hours: 연장 거래 시간 포함 여부 (기본값: True)
            outputsize: 출력 크기 ("compact": 최근 100개, "full": 전체)
            start_date: 시작 날짜 (필터링용)
            end_date: 종료 날짜 (필터링용)

        Returns:
            인트라데이 데이터 리스트 (datetime, open, high, low, close, volume)

        사용 예제:
            >>> data = await client.stock.intraday("AAPL", "5min")
            >>> print(f"조회된 데이터: {len(data)}개")
        """
        result = await self._call_core_stock_api(
            "TIME_SERIES_INTRADAY",
            symbol=symbol,
            interval=interval,
            adjusted=adjusted,
            extended_hours=extended_hours,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        return result if isinstance(result, list) else []

    async def daily(
        self,
        symbol: str,
        outputsize: Optional[Literal["compact", "full"]] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        일별 시계열 데이터를 가져옵니다

        20+ 년의 역사적 일별 OHLCV 데이터를 반환합니다.
        원시 (as-traded) 데이터로 제공됩니다.

        Args:
            symbol: 주식 심볼 (e.g., "AAPL")
            outputsize: 출력 크기 ("compact": 최근 100개, "full": 전체)
            start_date: 시작 날짜 (필터링용)
            end_date: 종료 날짜 (필터링용)

        Returns:
            일별 데이터 리스트 (date, open, high, low, close, volume)

        사용 예제:
            >>> data = await client.stock.daily("AAPL")
            >>> print(f"일별 데이터: {len(data)}개")
        """
        result = await self._call_core_stock_api(
            "TIME_SERIES_DAILY",
            symbol=symbol,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        return result if isinstance(result, list) else []

    async def daily_adjusted(
        self,
        symbol: str,
        outputsize: Optional[Literal["compact", "full"]] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        일별 조정 시계열 데이터를 가져옵니다

        원시 일별 OHLCV 값, 조정 종가, 역사적 주식 분할 및 배당 이벤트를 반환합니다.
        20+ 년의 역사적 데이터를 제공합니다.

        Args:
            symbol: 주식 심볼 (e.g., "AAPL")
            outputsize: 출력 크기 ("compact": 최근 100개, "full": 전체)
            start_date: 시작 날짜 (필터링용)
            end_date: 종료 날짜 (필터링용)

        Returns:
            조정된 일별 데이터 리스트 (date, open, high, low, close, adjusted_close, volume, dividend_amount, split_coefficient)

        사용 예제:
            >>> data = await client.stock.daily_adjusted("AAPL")
            >>> print(f"조정된 일별 데이터: {len(data)}개")
        """
        result = await self._call_core_stock_api(
            "TIME_SERIES_DAILY_ADJUSTED",
            symbol=symbol,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        return result if isinstance(result, list) else []

    async def weekly(
        self,
        symbol: str,
        outputsize: Optional[Literal["compact", "full"]] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get weekly time series data"""
        result = await self._call_core_stock_api(
            "TIME_SERIES_WEEKLY",
            symbol=symbol,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        return result if isinstance(result, list) else []

    async def weekly_adjusted(
        self,
        symbol: str,
        outputsize: Optional[Literal["compact", "full"]] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get weekly adjusted time series data"""
        result = await self._call_core_stock_api(
            "TIME_SERIES_WEEKLY_ADJUSTED",
            symbol=symbol,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        return result if isinstance(result, list) else []

    async def monthly(
        self,
        symbol: str,
        outputsize: Optional[Literal["compact", "full"]] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get monthly time series data"""
        result = await self._call_core_stock_api(
            "TIME_SERIES_MONTHLY",
            symbol=symbol,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        return result if isinstance(result, list) else []

    async def monthly_adjusted(
        self,
        symbol: str,
        outputsize: Optional[Literal["compact", "full"]] = "full",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get monthly adjusted time series data"""
        result = await self._call_core_stock_api(
            "TIME_SERIES_MONTHLY_ADJUSTED",
            symbol=symbol,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        return result if isinstance(result, list) else []

    async def quote(self, symbol: str) -> dict[str, Any]:
        """
        실시간 주가를 가져옵니다

        주어진 심볼의 최신 주가 정보를 반환합니다.
        시가, 고가, 저가, 종가, 거래량, 변동량 등을 포함합니다.

        Args:
            symbol: 주식 심볼 (e.g., "AAPL")

        Returns:
            실시간 주가 정보 딕셔너리

        사용 예제:
            >>> quote = await client.stock.quote("AAPL")
            >>> print(f"현재 가: ${quote['price']}")
        """
        result = await self._call_core_stock_api("GLOBAL_QUOTE", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def bulk_quotes(self) -> dict[str, Any]:
        """Get bulk real-time quotes"""
        result = await self._call_core_stock_api("REALTIME_BULK_QUOTES")
        return result if isinstance(result, dict) else {}

    async def search(self, keywords: str) -> list[dict[str, Any]]:
        """
        심볼을 검색합니다

        키워드로 주식, ETF 등의 심볼을 검색합니다.
        검색 결과는 유사도에 따라 정렬됩니다.

        Args:
            keywords: 검색 키워드 (e.g., "Apple", "AAPL")

        Returns:
            검색 결과 리스트 (심볼, 이름, 타입, 지역, 시장 정보 포함)

        사용 예제:
            >>> results = await client.stock.search("Apple")
            >>> for result in results:
            ...     print(f"{result['symbol']}: {result['name']}")
        """
        result = await self._call_core_stock_api("SYMBOL_SEARCH", keywords=keywords)
        return result if isinstance(result, list) else []

    async def market_status(self) -> dict[str, Any]:
        """
        글로벌 시장 상태를 가져옵니다

        전 세계 주요 주식 시장의 개장/폐장 상태를 반환합니다.
        리얼타임으로 업데이트됩니다.

        Returns:
            시장 상태 정보 딕셔너리

        사용 예제:
            >>> status = await client.stock.market_status()
            >>> print(f"시장 상태: {status}")
        """
        result = await self._call_core_stock_api("MARKET_STATUS")
        return result if isinstance(result, dict) else {}
