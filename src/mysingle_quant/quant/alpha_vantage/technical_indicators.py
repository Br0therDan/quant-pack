"""
Alpha Vantage API 클라이언트 - 기술적 지표 모듸

주가 차트 분석에 필요한 다양한 기술적 지표들을 제공합니다.
이동평균, 모멘텀 오실레이터, 변동성 지표 등을 포함하여
트레이딩 및 투자 결정에 도움이 되는 데이터를 제공합니다.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional

from .base import BaseAPIHandler

if TYPE_CHECKING:
    pass  # Remove circular import reference

logger = logging.getLogger(__name__)


class TechnicalIndicators(BaseAPIHandler):
    """
    Alpha Vantage 기술적 지표 API 핸들러

    주가 차트 분석에 사용되는 다양한 기술적 지표들을 제공합니다.
    모든 주요 기술적 지표들을 지원하며, 다양한 시간 간격으로 데이터를 제공합니다.

    지원하는 지표 카테고리:
    - 이동평균: SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3
    - 모멘텀 오실레이터: MACD, RSI, Stochastic, ADX, CCI, Aroon
    - 변동성 지표: Bollinger Bands, ATR
    - 거래량 지표: VWAP, OBV

    사용 예제:
        >>> client = AlphaVantageClient()
        >>> # 20일 단순이동평균
        >>> sma_data = await client.technical_indicators.sma(
        ...     symbol="AAPL",
        ...     interval="daily",
        ...     time_period=20
        ... )
        >>> # RSI 지표
        >>> rsi_data = await client.technical_indicators.rsi(
        ...     symbol="AAPL",
        ...     interval="daily",
        ...     time_period=14
        ... )
    """

    async def _call_technical_indicator(
        self,
        function: str,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Base method for calling technical indicator APIs"""

        params = {
            "function": function,
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
        }

        # Add additional parameters
        params.update(kwargs)

        data = await self._make_request(params)
        return self._parse_technical_indicator_response(data, function)

    def _parse_technical_indicator_response(
        self, data: dict[str, Any], function: str
    ) -> list[dict[str, Any]]:
        """Parse technical indicator API response"""

        # Find the technical analysis data key
        technical_data_key = None
        for key in data:
            if key.startswith("Technical Analysis:"):
                technical_data_key = key
                break

        if not technical_data_key:
            return []

        time_series = data.get(technical_data_key, {})
        result = []

        for date_str, values in time_series.items():
            try:
                # Try parsing as datetime first (for intraday)
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    time_field = "datetime"
                except ValueError:
                    # Parse as date (for daily/weekly/monthly)
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    time_field = "date"

                record: dict[str, Any] = {time_field: dt}

                # Add all indicator values
                for value_key, value in values.items():
                    # Clean the key name (remove numbering)
                    clean_key = value_key.split(". ", 1)[-1].lower().replace(" ", "_")
                    record[clean_key] = self._safe_float(value)

                result.append(record)

            except ValueError as e:
                logger.warning(f"Failed to parse date {date_str}: {e}")
                continue

        # Sort by time
        time_key = (
            "datetime" if "datetime" in result[0] else "date" if result else "date"
        )
        result.sort(key=lambda x: x.get(time_key, datetime.min))

        logger.info(f"Parsed {len(result)} {function} records")
        return result

    # Moving Averages
    async def sma(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Simple Moving Average"""
        return await self._call_technical_indicator(
            "SMA",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def ema(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Exponential Moving Average"""
        return await self._call_technical_indicator(
            "EMA",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def wma(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Weighted Moving Average"""
        return await self._call_technical_indicator(
            "WMA",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def dema(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Double Exponential Moving Average"""
        return await self._call_technical_indicator(
            "DEMA",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def tema(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Triple Exponential Moving Average"""
        return await self._call_technical_indicator(
            "TEMA",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def trima(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Triangular Moving Average"""
        return await self._call_technical_indicator(
            "TRIMA",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def kama(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Kaufman Adaptive Moving Average"""
        return await self._call_technical_indicator(
            "KAMA",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def mama(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        series_type: Literal["close", "open", "high", "low"] = "close",
        fastlimit: Optional[float] = None,
        slowlimit: Optional[float] = None,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """MESA Adaptive Moving Average"""
        kwargs = {"series_type": series_type}
        if fastlimit is not None:
            kwargs["fastlimit"] = str(fastlimit)
        if slowlimit is not None:
            kwargs["slowlimit"] = str(slowlimit)
        if month is not None:
            kwargs["month"] = month

        return await self._call_technical_indicator("MAMA", symbol, interval, **kwargs)

    async def vwap(
        self,
        symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"],
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Volume Weighted Average Price"""
        kwargs = {}
        if month is not None:
            kwargs["month"] = month

        return await self._call_technical_indicator("VWAP", symbol, interval, **kwargs)

    async def t3(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Triple Exponential Moving Average (T3)"""
        return await self._call_technical_indicator(
            "T3",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    # Oscillators
    async def macd(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        series_type: Literal["close", "open", "high", "low"] = "close",
        fastperiod: Optional[int] = None,
        slowperiod: Optional[int] = None,
        signalperiod: Optional[int] = None,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Moving Average Convergence Divergence"""
        kwargs = {"series_type": series_type}
        if fastperiod is not None:
            kwargs["fastperiod"] = str(fastperiod)
        if slowperiod is not None:
            kwargs["slowperiod"] = str(slowperiod)
        if signalperiod is not None:
            kwargs["signalperiod"] = str(signalperiod)
        if month is not None:
            kwargs["month"] = month

        return await self._call_technical_indicator("MACD", symbol, interval, **kwargs)

    async def rsi(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int = 14,
        series_type: Literal["close", "open", "high", "low"] = "close",
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Relative Strength Index"""
        return await self._call_technical_indicator(
            "RSI",
            symbol,
            interval,
            time_period=str(time_period),
            series_type=series_type,
            month=month,
        )

    async def stoch(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        fastkperiod: Optional[int] = None,
        slowkperiod: Optional[int] = None,
        slowdperiod: Optional[int] = None,
        slowkmatype: Optional[int] = None,
        slowdmatype: Optional[int] = None,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Stochastic Oscillator"""
        kwargs = {}
        if fastkperiod is not None:
            kwargs["fastkperiod"] = str(fastkperiod)
        if slowkperiod is not None:
            kwargs["slowkperiod"] = str(slowkperiod)
        if slowdperiod is not None:
            kwargs["slowdperiod"] = str(slowdperiod)
        if slowkmatype is not None:
            kwargs["slowkmatype"] = str(slowkmatype)
        if slowdmatype is not None:
            kwargs["slowdmatype"] = str(slowdmatype)
        if month is not None:
            kwargs["month"] = month

        return await self._call_technical_indicator("STOCH", symbol, interval, **kwargs)

    async def adx(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int = 14,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Average Directional Movement Index"""
        return await self._call_technical_indicator(
            "ADX", symbol, interval, time_period=str(time_period), month=month
        )

    async def cci(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int = 14,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Commodity Channel Index"""
        return await self._call_technical_indicator(
            "CCI", symbol, interval, time_period=str(time_period), month=month
        )

    async def aroon(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int = 14,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Aroon Indicator"""
        return await self._call_technical_indicator(
            "AROON", symbol, interval, time_period=str(time_period), month=month
        )

    async def bbands(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
        nbdevup: Optional[int] = None,
        nbdevdn: Optional[int] = None,
        matype: Optional[int] = None,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Bollinger Bands"""
        kwargs = {"time_period": str(time_period), "series_type": series_type}
        if nbdevup is not None:
            kwargs["nbdevup"] = str(nbdevup)
        if nbdevdn is not None:
            kwargs["nbdevdn"] = str(nbdevdn)
        if matype is not None:
            kwargs["matype"] = str(matype)
        if month is not None:
            kwargs["month"] = month

        return await self._call_technical_indicator(
            "BBANDS", symbol, interval, **kwargs
        )

    async def atr(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        time_period: int = 14,
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Average True Range"""
        return await self._call_technical_indicator(
            "ATR", symbol, interval, time_period=str(time_period), month=month
        )

    async def obv(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        month: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """On Balance Volume"""
        kwargs = {}
        if month is not None:
            kwargs["month"] = month

        return await self._call_technical_indicator("OBV", symbol, interval, **kwargs)
