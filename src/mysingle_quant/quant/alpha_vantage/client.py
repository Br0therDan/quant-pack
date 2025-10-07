"""
Alpha Vantage API 클라이언트 - 메인 클라이언트 모듈

Alpha Vantage API에 대한 통합 클라이언트를 제공합니다.
모든 API 카테고리에 대한 접근을 지원하며, 환경변수를 통한 API 키 관리를 제공합니다.

지원하는 API 카테고리:
- 주식 데이터 (stock)
- 기본 데이터 (fundamental)
- 기술 지표 (ti)
- 외환 (fx)
- 인텔리전스 (intelligence)
- 암호화폐 (crypto)
- 원자재 (commodities)
- 경제 지표 (economic_indicators)
- 옵션 데이터 (options)
"""

import logging
from typing import Any, Optional

import aiohttp

from ...core.config import settings
from .commodities import Commodities
from .core_stock import CoreStock
from .crypto import DigitalCryptoCurrencies
from .economic_indicators import EconomicIndicators
from .forex import ForeignExchange
from .fundamental import Fundamental
from .intelligence import Intelligence
from .options import Options
from .technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """
    Alpha Vantage API 클라이언트

    Alpha Vantage의 모든 API 엔드포인트에 대한 통합 액세스를 제공합니다.

    특징:
    - 비동기 HTTP 요청 지원
    - 자동 에러 처리 및 로깅
    - 모듈별 API 구성
    - 환경변수를 통한 API 키 관리

    문서: https://www.alphavantage.co/documentation/

    환경변수:
    - ALPHA_VANTAGE_API_KEY: Alpha Vantage API 키

    사용 예제:
        >>> client = AlphaVantageClient()  # 환경변수에서 API 키 로드
        >>> # 또는
        >>> client = AlphaVantageClient(api_key="your_api_key")
        >>>
        >>> # 주식 데이터 조회
        >>> data = await client.stock.time_series_daily("AAPL")
        >>>
        >>> # 세션 종료
        >>> await client.close()
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        """
        Alpha Vantage API 클라이언트 초기화

        Args:
            api_key: Alpha Vantage API 키. 제공되지 않으면
                    ALPHA_VANTAGE_API_KEY 환경변수에서 가져옵니다.

        Raises:
            ValueError: API 키가 제공되지 않고 ALPHA_VANTAGE_API_KEY
                       환경변수가 설정되지 않은 경우

        사용 예제:
            >>> # 환경변수에서 API 키 로드
            >>> client = AlphaVantageClient()
            >>>
            >>> # 직접 API 키 제공
            >>> client = AlphaVantageClient(api_key="your_key")
        """
        if api_key is None:
            api_key = settings.ALPHA_VANTAGE_API_KEY

        if not api_key:
            raise ValueError(
                "Alpha Vantage API key is required. "
                "Either pass it as a parameter or set the ALPHA_VANTAGE_API_KEY environment variable."
            )

        self.api_key = api_key
        self.session: aiohttp.ClientSession | None = None

        # Initialize API handlers
        self.stock = CoreStock(self)
        self.fundamental = Fundamental(self)
        self.ti = TechnicalIndicators(self)
        self.fx = ForeignExchange(self)
        self.intelligence = Intelligence(self)
        self.crypto = DigitalCryptoCurrencies(self)
        self.commodities = Commodities(self)
        self.economic_indicators = EconomicIndicators(self)
        self.options = Options(self)

    async def _get_session(self) -> aiohttp.ClientSession:
        """aiohttp 세션을 가져오거나 생성합니다"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """
        aiohttp 세션을 종료합니다

        클라이언트 사용을 완료한 후 리소스 정리를 위해 호출해야 합니다.

        사용 예제:
            >>> client = AlphaVantageClient()
            >>> # API 호출들...
            >>> await client.close()
        """
        if self.session and not self.session.closed:
            await self.session.close()

    async def _make_request(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        공통 에러 처리를 포함한 API 요청을 수행합니다

        Args:
            params: API 요청 파라미터

        Returns:
            API 응답 데이터

        Raises:
            ValueError: API 에러 메시지나 요청 제한이 발생한 경우
            aiohttp.ClientError: HTTP 요청 에러가 발생한 경우
        """
        # Add API key to parameters
        params["apikey"] = self.api_key

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

                return data

        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for request: {e}")
            raise
        except Exception as e:
            logger.error(f"Error for request: {e}")
            raise
