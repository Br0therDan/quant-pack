"""
Alpha Vantage API 클라이언트 - 외환(FX) 모듈

전 세계 주요 통화의 환율 데이터를 제공합니다.
실시간 환율, 인트라데이, 일별, 주별, 월별 데이터를 지원하며
168개 통화와 암호화폐 데이터를 포함합니다.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional

from .base import BaseAPIHandler

if TYPE_CHECKING:
    pass  # Remove circular import reference

logger = logging.getLogger(__name__)


class ForeignExchange(BaseAPIHandler):
    """
    Alpha Vantage 외환(FX) 데이터 API 핸들러

    전 세계 168개 통화 및 암호화폐의 환율 데이터를 제공합니다.
    실시간 환율부터 역사적 데이터까지 다양한 시간 간격으로
    제공하여 FX 트레이딩 및 분석에 필요한 데이터를 제공합니다.

    지원하는 기능:
    - 실시간 환율 조회
    - 인트라데이 FX 데이터 (1분, 5분, 15분, 30분, 60분)
    - 일별, 주별, 월별 FX 데이터
    - 168개 통화 지원 (USD, EUR, JPY, GBP, KRW 등)
    - 암호화폐 환율 데이터 지원

    사용 예제:
        >>> client = AlphaVantageClient()
        >>> # 실시간 USD/KRW 환율
        >>> rate = await client.forex.exchange_rate("USD", "KRW")
        >>> # EUR/USD 일별 데이터
        >>> daily_data = await client.forex.daily("EUR", "USD")
    """

    async def _call_fx_api(
        self,
        function: str,
        from_currency: Optional[str] = None,
        to_currency: Optional[str] = None,
        from_symbol: Optional[str] = None,
        to_symbol: Optional[str] = None,
        interval: Optional[str] = None,
        outputsize: Optional[str] = "full",
        **kwargs: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Base method for calling FX APIs"""

        # Validate required parameters
        if function == "CURRENCY_EXCHANGE_RATE":
            if not from_currency or not to_currency:
                raise ValueError(
                    "from_currency and to_currency parameters are required for CURRENCY_EXCHANGE_RATE"
                )
        elif function == "FX_INTRADAY":
            if not from_symbol or not to_symbol or not interval:
                raise ValueError(
                    "from_symbol, to_symbol, and interval parameters are required for FX_INTRADAY"
                )
        elif function in ["FX_DAILY", "FX_WEEKLY", "FX_MONTHLY"] and (
            not from_symbol or not to_symbol
        ):
            raise ValueError(
                f"from_symbol and to_symbol parameters are required for {function}"
            )

        # Build parameters
        params = {
            "function": function,
            "apikey": self.api_key,
        }

        # Add function-specific parameters
        if from_currency:
            params["from_currency"] = from_currency
        if to_currency:
            params["to_currency"] = to_currency
        if from_symbol:
            params["from_symbol"] = from_symbol
        if to_symbol:
            params["to_symbol"] = to_symbol
        if interval:
            params["interval"] = interval
        if outputsize:
            params["outputsize"] = outputsize

        # Add any additional parameters
        params.update(kwargs)

        data = await self._make_request(params)

        # Parse response based on function type
        return self._parse_fx_response(
            data,
            function,
            interval,
        )

    def _parse_fx_response(
        self,
        data: dict[str, Any],
        function: str,
        interval: Optional[str] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Parse FX API response based on function type"""

        if function == "CURRENCY_EXCHANGE_RATE":
            return self._parse_currency_exchange_rate(data)
        elif function == "FX_INTRADAY":
            return self._parse_fx_intraday(data, interval)
        elif function in ["FX_DAILY", "FX_WEEKLY", "FX_MONTHLY"]:
            return self._parse_fx_time_series(data, function)
        else:
            return data  # Return as-is for unknown functions

    def _parse_currency_exchange_rate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse real-time currency exchange rate response"""
        exchange_rate = data.get("Realtime Currency Exchange Rate", {})
        if not exchange_rate:
            return {}

        return {
            "from_currency_code": exchange_rate.get("1. From_Currency Code", ""),
            "from_currency_name": exchange_rate.get("2. From_Currency Name", ""),
            "to_currency_code": exchange_rate.get("3. To_Currency Code", ""),
            "to_currency_name": exchange_rate.get("4. To_Currency Name", ""),
            "exchange_rate": self._safe_float(exchange_rate.get("5. Exchange Rate")),
            "last_refreshed": exchange_rate.get("6. Last Refreshed", ""),
            "time_zone": exchange_rate.get("7. Time Zone", ""),
            "bid_price": self._safe_float(exchange_rate.get("8. Bid Price")),
            "ask_price": self._safe_float(exchange_rate.get("9. Ask Price")),
        }

    def _parse_fx_intraday(
        self,
        data: dict[str, Any],
        interval: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Parse FX intraday time series response"""
        if not interval:
            return []

        time_series_key = f"Time Series FX ({interval})"
        time_series = data.get(time_series_key, {})

        result = []
        for datetime_str, values in time_series.items():
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

            result.append(
                {
                    "datetime": dt,
                    "open": self._safe_float(values.get("1. open")),
                    "high": self._safe_float(values.get("2. high")),
                    "low": self._safe_float(values.get("3. low")),
                    "close": self._safe_float(values.get("4. close")),
                }
            )

        # Sort by datetime
        result.sort(key=lambda x: x["datetime"])

        logger.info(f"Parsed {len(result)} FX intraday records")
        return result

    def _parse_fx_time_series(
        self,
        data: dict[str, Any],
        function: str,
    ) -> list[dict[str, Any]]:
        """Parse FX time series response (daily, weekly, monthly)"""

        # Determine the time series key
        if function == "FX_DAILY":
            time_series_key = "Time Series FX (Daily)"
        elif function == "FX_WEEKLY":
            time_series_key = "Time Series FX (Weekly)"
        elif function == "FX_MONTHLY":
            time_series_key = "Time Series FX (Monthly)"
        else:
            return []

        time_series = data.get(time_series_key, {})

        result = []
        for date_str, values in time_series.items():
            dt = datetime.strptime(date_str, "%Y-%m-%d")

            result.append(
                {
                    "date": dt,
                    "open": self._safe_float(values.get("1. open")),
                    "high": self._safe_float(values.get("2. high")),
                    "low": self._safe_float(values.get("3. low")),
                    "close": self._safe_float(values.get("4. close")),
                }
            )

        # Sort by date
        result.sort(key=lambda x: x["date"])

        logger.info(f"Parsed {len(result)} FX {function.lower()} records")
        return result

    async def exchange_rate(
        self, from_currency: str, to_currency: str
    ) -> dict[str, Any]:
        """
        실시간 통화 환율을 가져옵니다.

        두 통화 간의 실시간 환율 정보를 제공합니다.
        168개 전세계 통화와 주요 암호화폐를 지원합니다.

        Args:
            from_currency: 기준 통화 코드 (예: "USD", "EUR", "KRW")
            to_currency: 대상 통화 코드 (예: "KRW", "JPY", "GBP")

        Returns:
            dict: 실시간 환율 정보를 포함한 딕셔너리
                 - from_currency_code: 기준 통화 코드
                 - from_currency_name: 기준 통화명
                 - to_currency_code: 대상 통화 코드
                 - to_currency_name: 대상 통화명
                 - exchange_rate: 현재 환율
                 - last_refreshed: 마지막 업데이트 시간
                 - time_zone: 시간대

        Example:
            >>> # USD 대비 KRW 환율
            >>> usd_krw = await client.forex.exchange_rate("USD", "KRW")
            >>> print(f"1 USD = {usd_krw['exchange_rate']} KRW")

            >>> # EUR 대비 USD 환율
            >>> eur_usd = await client.forex.exchange_rate("EUR", "USD")
            >>> print(f"1 EUR = {eur_usd['exchange_rate']} USD")

            >>> # 비트코인 대비 USD 환율
            >>> btc_usd = await client.forex.exchange_rate("BTC", "USD")
        """
        result = await self._call_fx_api(
            "CURRENCY_EXCHANGE_RATE",
            from_currency=from_currency,
            to_currency=to_currency,
        )
        return result if isinstance(result, dict) else {}

    async def intraday(
        self,
        from_symbol: str,
        to_symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"],
        outputsize: Literal["compact", "full"] = "compact",
    ) -> list[dict[str, Any]]:
        """
        인트라데이 FX 데이터를 가져옵니다.

        지정된 시간 간격에 따른 인트라데이 환율 데이터를 제공합니다.
        단기 FX 트레이딩 및 실시간 가격 분석에 유용합니다.

        Args:
            from_symbol: 기준 통화 코드 (예: "EUR", "GBP")
            to_symbol: 대상 통화 코드 (예: "USD", "JPY")
            interval: 데이터 간격 ("1min", "5min", "15min", "30min", "60min")
            outputsize: 출력 크기
                       - "compact": 최근 100개 데이터 포인트
                       - "full": 전체 데이터 (최대 20년)

        Returns:
            list: 인트라데이 FX 데이터 리스트
                  각 항목은 다음을 포함:
                  - datetime: 날짜 및 시간
                  - open: 시가
                  - high: 고가
                  - low: 저가
                  - close: 종가

        Example:
            >>> # EUR/USD 5분 간격 데이터
            >>> eur_usd_5m = await client.forex.intraday(
            ...     from_symbol="EUR",
            ...     to_symbol="USD",
            ...     interval="5min",
            ...     outputsize="compact"
            ... )
            >>>
            >>> # 최신 데이터 포인트 확인
            >>> latest = eur_usd_5m[0]
            >>> print(f"시간: {latest['datetime']}, 종가: {latest['close']}")
        """
        result = await self._call_fx_api(
            "FX_INTRADAY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            interval=interval,
            outputsize=outputsize,
        )
        return result if isinstance(result, list) else []

    async def daily(
        self,
        from_symbol: str,
        to_symbol: str,
        outputsize: Literal["compact", "full"] = "compact",
    ) -> list[dict[str, Any]]:
        """
        일별 FX 데이터를 가져옵니다.

        지정된 통화 쌍의 일별 환율 데이터를 제공합니다.
        장기 트렌드 분석 및 주간 패턴 연구에 적합합니다.

        Args:
            from_symbol: 기준 통화 코드 (예: "EUR", "GBP")
            to_symbol: 대상 통화 코드 (예: "USD", "JPY")
            outputsize: 출력 크기
                       - "compact": 최근 100일 데이터
                       - "full": 전체 데이터 (최대 20년)

        Returns:
            list: 일별 FX 데이터 리스트
                  각 항목은 다음을 포함:
                  - date: 날짜
                  - open: 시가
                  - high: 고가
                  - low: 저가
                  - close: 종가

        Example:
            >>> # EUR/USD 일별 데이터 (최근 100일)
            >>> eur_usd_daily = await client.forex.daily(
            ...     from_symbol="EUR",
            ...     to_symbol="USD",
            ...     outputsize="compact"
            ... )
            >>>
            >>> # 월별 수익률 계산
            >>> monthly_returns = []
            >>> for i in range(0, len(eur_usd_daily), 30):
            ...     if i + 30 < len(eur_usd_daily):
            ...         start_price = eur_usd_daily[i + 30]['close']
            ...         end_price = eur_usd_daily[i]['close']
            ...         monthly_return = (end_price - start_price) / start_price * 100
            ...         monthly_returns.append(monthly_return)
        """
        result = await self._call_fx_api(
            "FX_DAILY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            outputsize=outputsize,
        )
        return result if isinstance(result, list) else []

    async def weekly(
        self,
        from_symbol: str,
        to_symbol: str,
    ) -> list[dict[str, Any]]:
        """
        주별 FX 데이터를 가져옵니다.

        지정된 통화 쌍의 주별 환율 데이터를 제공합니다.
        매주 마지막 거래일의 데이터로 구성되며, 장기 추세 분석에 유용합니다.

        Args:
            from_symbol: 기준 통화 코드 (예: "EUR", "GBP")
            to_symbol: 대상 통화 코드 (예: "USD", "JPY")

        Returns:
            list: 주별 FX 데이터 리스트
                  각 항목은 다음을 포함:
                  - date: 날짜 (주의 마지막 거래일)
                  - open: 주 시가
                  - high: 주 고가
                  - low: 주 저가
                  - close: 주 종가

        Example:
            >>> # EUR/USD 주별 데이터
            >>> eur_usd_weekly = await client.forex.weekly(
            ...     from_symbol="EUR",
            ...     to_symbol="USD"
            ... )
            >>>
            >>> # 주간 변동성 계산
            >>> for week_data in eur_usd_weekly[:10]:
            ...     volatility = (week_data['high'] - week_data['low']) / week_data['open'] * 100
            ...     print(f"주간 변동성: {volatility:.2f}%")
        """
        result = await self._call_fx_api(
            "FX_WEEKLY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
        )
        return result if isinstance(result, list) else []

    async def monthly(
        self,
        from_symbol: str,
        to_symbol: str,
    ) -> list[dict[str, Any]]:
        """
        월별 FX 데이터를 가져옵니다.

        지정된 통화 쌍의 월별 환율 데이터를 제공합니다.
        매월 마지막 거래일의 데이터로 구성되며, 장기 전략 수립과
        거시경제 분석에 적합합니다.

        Args:
            from_symbol: 기준 통화 코드 (예: "EUR", "GBP")
            to_symbol: 대상 통화 코드 (예: "USD", "JPY")

        Returns:
            list: 월별 FX 데이터 리스트
                  각 항목은 다음을 포함:
                  - date: 날짜 (월의 마지막 거래일)
                  - open: 월 시가
                  - high: 월 고가
                  - low: 월 저가
                  - close: 월 종가

        Example:
            >>> # EUR/USD 월별 데이터
            >>> eur_usd_monthly = await client.forex.monthly(
            ...     from_symbol="EUR",
            ...     to_symbol="USD"
            ... )
            >>>
            >>> # 연간 수익률 계산
            >>> yearly_returns = []
            >>> for i in range(0, len(eur_usd_monthly), 12):
            ...     if i + 12 < len(eur_usd_monthly):
            ...         start_price = eur_usd_monthly[i + 12]['close']
            ...         end_price = eur_usd_monthly[i]['close']
            ...         annual_return = (end_price - start_price) / start_price * 100
            ...         yearly_returns.append(annual_return)
        """
        result = await self._call_fx_api(
            "FX_MONTHLY",
            from_symbol=from_symbol,
            to_symbol=to_symbol,
        )
        return result if isinstance(result, list) else []
