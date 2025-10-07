"""
Alpha Vantage API 클라이언트 - 디지털 및 암호화폐 모듈

비트코인, 이더리움 등 주요 암호화폐의 실시간 및 역사적 데이터를 제공합니다.
암호화폐-법정화폐 간 환율, 인트라데이 데이터, 시계열 데이터를 지원하며
암호화폐 투자 및 분석에 필요한 모든 데이터를 제공합니다.
"""

import logging
from typing import Any, Literal, Optional

from .base import BaseAPIHandler

logger = logging.getLogger(__name__)


class DigitalCryptoCurrencies(BaseAPIHandler):
    """
    Alpha Vantage 디지털 및 암호화폐 API 핸들러

    비트코인, 이더리움, 라이트코인 등 주요 암호화폐의 실시간 및 역사적
    데이터를 제공하는 API 집합입니다. 암호화폐 및 디지털 통화 쌍의
    환율, 인트라데이 데이터, 역사적 시계열 데이터를 제공합니다.

    지원하는 기능:
    - 실시간 암호화폐/법정화폐 환율
    - 인트라데이 암호화폐 데이터 (1분, 5분, 15분, 30분, 60분)
    - 일별, 주별, 월별 역사적 데이터
    - 비트코인, 이더리움 특화 기능
    - 600개 이상의 암호화폐 지원

    사용 예제:
        >>> client = AlphaVantageClient()
        >>> # 비트코인 가격 조회
        >>> btc_price = await client.crypto.get_bitcoin_price()
        >>> # 이더리웄 일별 데이터
        >>> eth_daily = await client.crypto.digital_currency_daily("ETH", "USD")
    """

    async def currency_exchange_rate(
        self, from_currency: str, to_currency: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        암호화폐 또는 법정화폐 간의 실시간 환율을 가져옵니다.

        어떤 암호화폐 또는 법정화폐 쌍의 실시간 환율을 제공합니다.
        600개 이상의 암호화폐와 전세계 주요 법정화폐를 지원합니다.

        Args:
            from_currency: 기준 통화 (예: "BTC", "ETH", "USD")
                          암호화폐 또는 법정화폐 모두 가능
            to_currency: 대상 통화 (예: "USD", "EUR", "BTC")
                        암호화폐 또는 법정화폐 모두 가능
            **kwargs: API에 전달되는 추가 매개변수

        Returns:
            dict: 실시간 환율 데이터를 포함한 딕셔너리
                 - from_currency_code: 기준 통화 코드
                 - from_currency_name: 기준 통화명
                 - to_currency_code: 대상 통화 코드
                 - to_currency_name: 대상 통화명
                 - exchange_rate: 현재 환율
                 - last_refreshed: 마지막 업데이트 시간
                 - time_zone: 시간대

        Example:
            >>> # 비트코인 대비 유로 환율
            >>> btc_eur = await client.crypto.currency_exchange_rate(
            ...     from_currency="BTC",
            ...     to_currency="EUR"
            ... )
            >>> print(f"1 BTC = {btc_eur['exchange_rate']} EUR")

            >>> # 미국 달러 대비 일본 엔 환율
            >>> usd_jpy = await client.crypto.currency_exchange_rate(
            ...     from_currency="USD",
            ...     to_currency="JPY"
            ... )

            >>> # 이더리움 대비 비트코인 환율
            >>> eth_btc = await client.crypto.currency_exchange_rate(
            ...     from_currency="ETH",
            ...     to_currency="BTC"
            ... )
        """
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            **kwargs,
        }
        return await self.client._make_request(params)

    async def crypto_intraday(
        self,
        symbol: str,
        market: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"],
        outputsize: Optional[Literal["compact", "full"]] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        암호화폐의 인트라데이 데이터를 가져옵니다.

        지정된 암호화폐의 실시간 인트라데이 데이터를 제공합니다.
        이 기능은 프리미엄 API 기능입니다.

        Args:
            symbol: 암호화폐 심볼 (예: "ETH", "BTC", "LTC")
            market: 거래소 시장 (예: "USD", "EUR", "BTC")
            interval: 데이터 간격
                     - "1min": 1분 간격
                     - "5min": 5분 간격
                     - "15min": 15분 간격
                     - "30min": 30분 간격
                     - "60min": 60분 간격
            outputsize: 출력 크기
                       - "compact": 최근 100개 데이터 포인트
                       - "full": 전체 인트라데이 데이터
            **kwargs: API에 전달되는 추가 매개변수

        Returns:
            dict: 인트라데이 시계열 데이터를 포함한 딕셔너리
                  - 시간별 가격 데이터 (open, high, low, close, volume)
                  - 시장별 및 USD 기준 가격 정보

        Example:
            >>> # 이더리움 5분 간격 데이터
            >>> eth_intraday = await client.crypto.crypto_intraday(
            ...     symbol="ETH",
            ...     market="USD",
            ...     interval="5min",
            ...     outputsize="compact"
            ... )
            >>>
            >>> # 비트코인 1분 간격 데이터
            >>> btc_1min = await client.crypto.crypto_intraday(
            ...     symbol="BTC",
            ...     market="USD",
            ...     interval="1min"
            ... )
        """
        params = {
            "function": "CRYPTO_INTRADAY",
            "symbol": symbol,
            "market": market,
            "interval": interval,
            **kwargs,
        }
        if outputsize is not None:
            params["outputsize"] = outputsize

        return await self.client._make_request(params)

    async def digital_currency_daily(
        self, symbol: str, market: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        일일 디지털 화폐 시계열 데이터를 조회합니다.

        주요 암호화폐의 일일 종가, 거래량, 시가총액 등의
        역사적 데이터를 제공합니다.

        Args:
            symbol (str): 암호화폐 심볼 (예: 'BTC', 'ETH', 'LTC')
            market (str): 대상 시장 통화 (예: 'USD', 'EUR', 'GBP', 'JPY', 'KRW')
            **kwargs: API에 전달되는 추가 매개변수

        Returns:
            dict: 일일 암호화폐 데이터
                - 'Meta Data': 메타데이터 (심볼, 시장, 타임존 등)
                - 'Time Series (Digital Currency Daily)': 일일 시계열 데이터
                  각 날짜별로 다음 데이터 포함:
                  - open: 시가
                  - high: 고가
                  - low: 저가
                  - close: 종가
                  - volume: 거래량
                  - market cap: 시가총액

        Example:
            >>> crypto_client = CryptoClient(api_key="your_api_key")
            >>> # 비트코인 일일 데이터 조회
            >>> btc_daily = await crypto_client.digital_currency_daily('BTC', 'USD')
            >>> print(btc_daily['Meta Data']['2. Digital Currency Code'])
            'BTC'

            >>> # 이더리움 원화 기준 일일 데이터
            >>> eth_krw = await crypto_client.digital_currency_daily('ETH', 'KRW')
            >>> recent_date = list(eth_krw['Time Series (Digital Currency Daily)'].keys())[0]
            >>> print(f"최근 ETH 종가: {eth_krw['Time Series (Digital Currency Daily)'][recent_date]['4a. close (KRW)']}")
        """
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            **kwargs,
        }
        return await self.client._make_request(params)

    async def digital_currency_weekly(
        self, symbol: str, market: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        주간 디지털 화폐 시계열 데이터를 조회합니다.

        암호화폐의 주간 단위 집계 데이터로 장기 트렌드 분석과
        주간 단위 투자 전략 수립에 활용할 수 있습니다.

        Args:
            symbol (str): 암호화폐 심볼 (예: 'BTC', 'ETH', 'ADA')
            market (str): 대상 시장 통화 (예: 'USD', 'EUR', 'GBP', 'CNY', 'JPY')
            **kwargs: API에 전달되는 추가 매개변수

        Returns:
            dict: 주간 암호화폐 데이터
                - 'Meta Data': 메타데이터 (심볼, 시장, 마지막 갱신 등)
                - 'Time Series (Digital Currency Weekly)': 주간 시계열 데이터
                  각 주차별로 다음 데이터 포함:
                  - open: 주 시가
                  - high: 주 고가
                  - low: 주 저가
                  - close: 주 종가
                  - volume: 주간 총 거래량
                  - market cap: 주말 시가총액

        Example:
            >>> crypto_client = CryptoClient(api_key="your_api_key")
            >>> # 비트코인 주간 데이터로 장기 트렌드 분석
            >>> btc_weekly = await crypto_client.digital_currency_weekly('BTC', 'USD')
            >>>
            >>> # 최근 4주간 데이터 분석
            >>> weekly_data = btc_weekly['Time Series (Digital Currency Weekly)']
            >>> recent_weeks = list(weekly_data.keys())[:4]
            >>> for week in recent_weeks:
            >>>     close_price = weekly_data[week]['4a. close (USD)']
            >>>     print(f"{week}: ${close_price}")

            >>> # 라이트코인 유로 기준 주간 분석
            >>> ltc_eur = await crypto_client.digital_currency_weekly('LTC', 'EUR')
        """
        params = {
            "function": "DIGITAL_CURRENCY_WEEKLY",
            "symbol": symbol,
            "market": market,
            **kwargs,
        }
        return await self.client._make_request(params)

    async def digital_currency_monthly(
        self, symbol: str, market: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        월간 디지털 화폐 시계열 데이터를 조회합니다.

        암호화폐의 월간 단위 집계 데이터로 장기 투자 분석과
        계절성 패턴, 연간 성과 평가에 활용할 수 있습니다.

        Args:
            symbol (str): 암호화폐 심볼 (예: 'BTC', 'ETH', 'XRP')
            market (str): 대상 시장 통화 (예: 'USD', 'EUR', 'GBP', 'AUD', 'CAD')
            **kwargs: API에 전달되는 추가 매개변수

        Returns:
            dict: 월간 암호화폐 데이터
                - 'Meta Data': 메타데이터 (심볼, 시장, 데이터 소스 등)
                - 'Time Series (Digital Currency Monthly)': 월간 시계열 데이터
                  각 월별로 다음 데이터 포함:
                  - open: 월 시가
                  - high: 월 고가
                  - low: 월 저가
                  - close: 월 종가
                  - volume: 월간 총 거래량
                  - market cap: 월말 시가총액

        Example:
            >>> crypto_client = CryptoClient(api_key="your_api_key")
            >>> # 비트코인 월간 데이터로 연간 성과 분석
            >>> btc_monthly = await crypto_client.digital_currency_monthly('BTC', 'USD')
            >>>
            >>> # 최근 12개월 성과 계산
            >>> monthly_data = btc_monthly['Time Series (Digital Currency Monthly)']
            >>> months = list(monthly_data.keys())[:12]
            >>> first_month = monthly_data[months[-1]]['1a. open (USD)']
            >>> last_month = monthly_data[months[0]]['4a. close (USD)']
            >>> yearly_return = (float(last_month) / float(first_month) - 1) * 100
            >>> print(f"12개월 수익률: {yearly_return:.2f}%")

            >>> # 이더리움 월간 변동성 분석
            >>> eth_monthly = await crypto_client.digital_currency_monthly('ETH', 'USD')
        """
        params = {
            "function": "DIGITAL_CURRENCY_MONTHLY",
            "symbol": symbol,
            "market": market,
            **kwargs,
        }
        return await self.client._make_request(params)

    # Convenience methods for common use cases
    async def get_bitcoin_price(
        self,
        market: str = "USD",
        period: Literal["daily", "weekly", "monthly"] = "daily",
    ) -> dict[str, Any]:
        """
        비트코인 가격 데이터를 조회하는 편의 메서드입니다.

        비트코인의 일일, 주간, 월간 가격 데이터를 간편하게 조회할 수 있으며
        다양한 법정화폐 기준으로 가격 정보를 제공합니다.

        Args:
            market (str, optional): 시장 통화. 기본값은 'USD'
                                   주요 지원 통화: USD, EUR, GBP, JPY, KRW, CNY
            period (str, optional): 시간 주기. 기본값은 'daily'
                                   - 'daily': 일일 데이터
                                   - 'weekly': 주간 데이터
                                   - 'monthly': 월간 데이터

        Returns:
            dict: 비트코인 가격 데이터
                선택한 기간에 따라 해당하는 시계열 데이터 반환

        Raises:
            ValueError: period가 'daily', 'weekly', 'monthly' 중 하나가 아닌 경우

        Example:
            >>> crypto_client = CryptoClient(api_key="your_api_key")
            >>> # 비트코인 일일 USD 가격
            >>> btc_usd = await crypto_client.get_bitcoin_price()
            >>>
            >>> # 비트코인 주간 원화 가격
            >>> btc_krw_weekly = await crypto_client.get_bitcoin_price(
            ...     market="KRW",
            ...     period="weekly"
            ... )
            >>>
            >>> # 비트코인 월간 유로 가격으로 장기 트렌드 분석
            >>> btc_eur_monthly = await crypto_client.get_bitcoin_price(
            ...     market="EUR",
            ...     period="monthly"
            ... )
        """
        if period == "daily":
            return await self.digital_currency_daily("BTC", market)
        elif period == "weekly":
            return await self.digital_currency_weekly("BTC", market)
        elif period == "monthly":
            return await self.digital_currency_monthly("BTC", market)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    async def get_ethereum_price(
        self,
        market: str = "USD",
        period: Literal["daily", "weekly", "monthly"] = "daily",
    ) -> dict[str, Any]:
        """
        이더리움 가격 데이터를 조회하는 편의 메서드입니다.

        이더리움의 일일, 주간, 월간 가격 데이터를 간편하게 조회할 수 있으며
        DeFi 생태계 분석과 스마트 컨트랙트 플랫폼 투자 분석에 활용됩니다.

        Args:
            market (str, optional): 시장 통화. 기본값은 'USD'
                                   글로벌 통화 지원: USD, EUR, GBP, JPY, KRW, AUD
            period (str, optional): 시간 주기. 기본값은 'daily'
                                   - 'daily': 일일 가격 데이터
                                   - 'weekly': 주간 집계 데이터
                                   - 'monthly': 월간 집계 데이터

        Returns:
            dict: 이더리움 가격 데이터
                선택한 기간과 통화에 따른 상세한 시계열 데이터

        Raises:
            ValueError: period가 유효하지 않은 값인 경우

        Example:
            >>> crypto_client = CryptoClient(api_key="your_api_key")
            >>> # 이더리움 일일 USD 가격
            >>> eth_usd = await crypto_client.get_ethereum_price()
            >>>
            >>> # 이더리움 주간 원화 가격으로 DeFi 트렌드 분석
            >>> eth_krw_weekly = await crypto_client.get_ethereum_price(
            ...     market="KRW",
            ...     period="weekly"
            ... )
            >>>
            >>> # 이더리움 월간 유로 가격으로 연간 성과 분석
            >>> eth_eur_monthly = await crypto_client.get_ethereum_price(
            ...     market="EUR",
            ...     period="monthly"
            ... )
            >>>
            >>> # 이더리움 vs 비트코인 성과 비교 분석
            >>> eth_data = await crypto_client.get_ethereum_price(period="monthly")
            >>> btc_data = await crypto_client.get_bitcoin_price(period="monthly")
        """
        if period == "daily":
            return await self.digital_currency_daily("ETH", market)
        elif period == "weekly":
            return await self.digital_currency_weekly("ETH", market)
        elif period == "monthly":
            return await self.digital_currency_monthly("ETH", market)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    async def get_crypto_exchange_rates(
        self, crypto_symbols: list[str], target_currency: str = "USD"
    ) -> dict[str, dict[str, Any]]:
        """
        여러 암호화폐의 환율을 일괄 조회하는 편의 메서드입니다.

        포트폴리오 관리, 다중 암호화폐 비교 분석, 실시간 환율 모니터링에
        활용할 수 있는 일괄 환율 조회 기능을 제공합니다.

        Args:
            crypto_symbols (list[str]): 조회할 암호화폐 심볼 리스트
                                       예: ['BTC', 'ETH', 'LTC', 'XRP', 'ADA']
            target_currency (str, optional): 목표 통화. 기본값은 'USD'
                                            지원 통화: USD, EUR, GBP, JPY, KRW 등

        Returns:
            dict: 암호화폐별 환율 데이터
                각 심볼을 키로 하고, 환율 정보 또는 오류 정보를 값으로 하는 딕셔너리
                성공시: {'BTC': {환율 데이터}, 'ETH': {환율 데이터}, ...}
                오류시: {'심볼': {'error': '오류 메시지'}, ...}

        Example:
            >>> crypto_client = CryptoClient(api_key="your_api_key")
            >>> # 주요 암호화폐 USD 환율 일괄 조회
            >>> major_cryptos = ['BTC', 'ETH', 'LTC', 'XRP']
            >>> rates_usd = await crypto_client.get_crypto_exchange_rates(major_cryptos)
            >>>
            >>> for symbol, data in rates_usd.items():
            ...     if 'error' not in data:
            ...         rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
            ...         print(f"{symbol}/USD: {rate}")

            >>> # 암호화폐 원화 환율로 국내 투자자 포트폴리오 평가
            >>> portfolio = ['BTC', 'ETH', 'ADA', 'DOT']
            >>> rates_krw = await crypto_client.get_crypto_exchange_rates(
            ...     crypto_symbols=portfolio,
            ...     target_currency="KRW"
            ... )

            >>> # 유로 기준 암호화폐 환율로 유럽 시장 분석
            >>> rates_eur = await crypto_client.get_crypto_exchange_rates(
            ...     crypto_symbols=['BTC', 'ETH', 'USDT'],
            ...     target_currency="EUR"
            ... )
        """
        results = {}
        for symbol in crypto_symbols:
            try:
                result = await self.currency_exchange_rate(symbol, target_currency)
                results[symbol] = result
            except Exception as e:
                logger.error(f"Failed to get exchange rate for {symbol}: {e}")
                results[symbol] = {"error": str(e)}

        return results
