"""
Alpha Vantage API 클라이언트 - Alpha Intelligence™ 모듈

시장 인텔리전스 및 고급 분석 API를 제공합니다.
뉴스 감정 분석, 실적 발표 컨퍼런스 내용, 시장 동향 분석 등
고급 인텔리전스 기능을 제공합니다.

지원하는 기능:
- 뉴스 및 감정 분석
- 실적 발표 컨퍼런스 내용
- 상승/하락 및 거래량 상위 종목
- 내부자 거래 내역
- 고급 애널리틱스 (고정 및 슬라이딩 윈도우)
"""

import logging
from typing import Any, Literal, Optional

from .base import BaseAPIHandler

logger = logging.getLogger(__name__)


class Intelligence(BaseAPIHandler):
    """
    Alpha Intelligence™ API 핸들러

    Alpha Vantage의 고급 시장 인텔리전스 및 분석 API에 대한 인터페이스를 제공합니다.
    AI 기반 뉴스 감정 분석, 실적 발표 내용, 내부자 거래 등
    고급 인텔리전스 기능을 제공합니다.

    지원하는 API 기능:
    - NEWS_SENTIMENT: 뉴스 및 감정 분석
    - TRANSCRIPT: 실적 발표 컨퍼런스 내용
    - TOP_GAINERS_LOSERS: 상승/하락/거래량 상위 종목
    - INSIDER_TRANSACTIONS: 내부자 거래 내역
    - ANALYTICS_FIXED_WINDOW: 고정 기간 분석
    - ANALYTICS_SLIDING_WINDOW: 슬라이딩 윈도우 분석

    사용 예제:
        >>> client = AlphaVantageClient()
        >>> # 뉴스 감정 분석
        >>> news = await client.intelligence.news_sentiment(tickers="AAPL")
        >>> # 시장 동향 조회
        >>> movers = await client.intelligence.top_gainers_losers()
    """

    async def news_sentiment(
        self,
        tickers: Optional[str] = None,
        topics: Optional[str] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        sort: str = "LATEST",
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        실시간 및 과거 시장 뉴스 감정 분석 데이터를 가져옵니다.

        AI 기반 감정 분석을 통해 뉴스 기사가 주식 시장에 미치는 영향을
        정량적으로 측정합니다. 개별 종목이나 특정 주제별 뉴스의
        감정 점수와 관련성 점수를 제공합니다.

        Args:
            tickers: 조회할 주식/암호화폐 심볼 (쉼표로 구분)
                    예: "AAPL,TSLA,MSFT"
            topics: 뉴스 주제 필터 (쉼표로 구분)
                   예: "blockchain,earnings,ipo,mergers_and_acquisitions"
            time_from: 시작 날짜 및 시간 (YYYYMMDDTHHMM 형식)
                      예: "20220410T0130"
            time_to: 종료 날짜 및 시간 (YYYYMMDDTHHMM 형식)
                    예: "20220410T0530"
            sort: 정렬 순서 ("LATEST", "EARLIEST", "RELEVANCE")
            limit: 반환할 결과 수 (1-1000)

        Returns:
            Dict: 뉴스 기사와 감정 점수를 포함한 딕셔너리
                 - items: 뉴스 기사 목록
                 - sentiment_score_definition: 감정 점수 정의
                 - relevance_score_definition: 관련성 점수 정의

        Example:
            >>> # 애플 관련 최신 뉴스 10개 조회
            >>> news = await client.intelligence.news_sentiment(
            ...     tickers="AAPL",
            ...     limit=10
            ... )
            >>> # 특정 기간 암호화폐 뉴스 조회
            >>> crypto_news = await client.intelligence.news_sentiment(
            ...     topics="blockchain",
            ...     time_from="20240101T0000",
            ...     time_to="20240131T2359"
            ... )
        """
        params = {
            "function": "NEWS_SENTIMENT",
            "sort": sort,
            "limit": str(limit),
        }

        if tickers:
            params["tickers"] = tickers
        if topics:
            params["topics"] = topics
        if time_from:
            params["time_from"] = time_from
        if time_to:
            params["time_to"] = time_to

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
        실시간 상승률, 하락률, 거래량 상위 종목을 조회합니다.

        미국 주식 시장에서 당일 가장 높은 상승률을 보인 종목,
        가장 큰 하락률을 보인 종목, 그리고 가장 활발하게 거래된
        종목들의 목록을 실시간으로 제공합니다.

        Returns:
            Dict: 시장 동향 데이터를 포함한 딕셔너리
                 - top_gainers: 상승률 상위 종목 리스트
                 - top_losers: 하락률 상위 종목 리스트
                 - most_actively_traded: 거래량 상위 종목 리스트
                 - last_updated: 마지막 업데이트 시간

        각 종목 정보:
            - ticker: 종목 심볼
            - price: 현재 가격
            - change_amount: 변동 금액
            - change_percentage: 변동률 (%)
            - volume: 거래량

        Example:
            >>> # 오늘의 시장 동향 조회
            >>> movers = await client.intelligence.top_gainers_losers()
            >>> print(f"상승률 1위: {movers['top_gainers'][0]['ticker']}")
            >>> print(f"하락률 1위: {movers['top_losers'][0]['ticker']}")
            >>> print(f"거래량 1위: {movers['most_actively_traded'][0]['ticker']}")
        """
        params = {"function": "TOP_GAINERS_LOSERS"}

        return await self.client._make_request(params)

    async def insider_transactions(self, symbol: str) -> dict[str, Any]:
        """
        특정 종목의 내부자 거래 내역을 조회합니다.

        경영진, 이사회 구성원, 대주주 등의 내부자 거래 정보를 제공합니다.
        거래 일자, 거래 유형(매수/매도), 거래량, 가격 등의 상세 정보를
        포함하여 시장 인사이트를 제공합니다.

        Args:
            symbol: 조회할 주식 심볼 (예: "IBM", "AAPL")

        Returns:
            dict: 내부자 거래 내역을 포함한 딕셔너리
                 - symbol: 종목 심볼
                 - transactions: 거래 내역 리스트
                 - last_updated: 마지막 업데이트 시간

        각 거래 정보:
            - insider_name: 내부자 이름
            - title: 직책
            - transaction_date: 거래 날짜
            - transaction_type: 거래 유형 (Purchase/Sale)
            - shares: 거래 주식 수
            - price: 거래 가격

        Example:
            >>> # IBM의 내부자 거래 내역 조회
            >>> insider_trades = await client.intelligence.insider_transactions("IBM")
            >>> for trade in insider_trades['transactions'][:5]:
            ...     print(f"{trade['insider_name']}: {trade['transaction_type']} {trade['shares']} shares")
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
        여러 종목 간의 상관관계 분석을 위한 편의 메서드입니다.

        여러 주식 종목들 간의 가격 상관관계를 분석하여 포트폴리오 구성
        및 위험 분산 전략 수립에 필요한 정보를 제공합니다.

        Args:
            symbols: 분석할 종목들 (쉼표로 구분, 예: "AAPL,MSFT,IBM")
            range_param: 분석 기간 (기본값: "1year")
            interval: 데이터 간격 ("DAILY", "WEEKLY", "MONTHLY")

        Returns:
            dict: 상관관계 매트릭스와 기본 통계를 포함한 딕셔너리
                 - correlations: 종목 간 상관계수 매트릭스
                 - statistics: 평균, 표준편차 등 기본 통계

        Example:
            >>> # 애플, 마이크로소프트, IBM 상관관계 분석
            >>> corr = await client.intelligence.correlation_analysis(
            ...     symbols="AAPL,MSFT,IBM",
            ...     range_param="1year"
            ... )
            >>> print(corr['correlations'])
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
        단일 종목의 위험 분석을 위한 편의 메서드입니다.

        특정 종목의 변동성, 수익률, 샤프 비율 등 다양한 위험 지표를
        계산하여 투자 위험도를 평가할 수 있는 정보를 제공합니다.

        Args:
            symbol: 분석할 종목 심볼 (예: "AAPL")
            range_param: 분석 기간 (기본값: "1year")
            interval: 데이터 간격 ("DAILY", "WEEKLY", "MONTHLY")

        Returns:
            dict: 위험 지표들을 포함한 딕셔너리
                 - variance: 분산
                 - standard_deviation: 표준편차
                 - mean_return: 평균 수익률
                 - cumulative_return: 누적 수익률
                 - sharpe_ratio: 샤프 비율

        Example:
            >>> # 애플 주식의 위험 지표 분석
            >>> risk = await client.intelligence.risk_metrics(
            ...     symbol="AAPL",
            ...     range_param="1year"
            ... )
            >>> print(f"변동성: {risk['standard_deviation']}")
            >>> print(f"샤프비율: {risk['sharpe_ratio']}")
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
        롤링 변동성 분석을 위한 편의 메서드입니다.

        지정된 윈도우 크기로 이동하면서 계산되는 변동성을 제공합니다.
        시간에 따른 변동성 변화를 추적하여 시장 상황 변화를
        모니터링할 수 있습니다.

        Args:
            symbol: 분석할 종목 심볼 (예: "AAPL")
            window_size: 롤링 윈도우 크기 (기본값: 20일)
            range_param: 분석 기간 (기본값: "3month")
            interval: 데이터 간격 ("DAILY", "WEEKLY")

        Returns:
            dict: 롤링 변동성 지표를 포함한 딕셔너리
                 - time_series: 시간별 변동성 데이터
                 - rolling_volatility: 각 시점의 롤링 변동성

        Example:
            >>> # 애플 주식의 20일 롤링 변동성 분석
            >>> vol = await client.intelligence.rolling_volatility(
            ...     symbol="AAPL",
            ...     window_size=20,
            ...     range_param="3month"
            ... )
            >>> print("시간별 변동성 변화:")
            >>> for data in vol['time_series'][:5]:
            ...     print(f"{data['date']}: {data['volatility']}")
        """
        return await self.analytics_sliding_window(
            symbols=symbol,
            range_param=range_param,
            interval=interval,
            window_size=window_size,
            ohlc="close",
            calculations="STDDEV",
        )
