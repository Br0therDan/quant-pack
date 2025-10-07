"""
Alpha Vantage API 클라이언트 - 옵션 데이터 모듸

미국 옵션 마켓의 실시간 및 과거 데이터를 제공합니다.
15년 이상의 역사적 데이터와 전체 시장 커버리지를 제공합니다.

문서: https://www.alphavantage.co/documentation/#options
"""

from typing import Any, Literal, Optional

from .base import BaseAPIHandler


class Options(BaseAPIHandler):
    """
    Alpha Vantage 옵션 데이터 API 핸들러

    미국 옵션 마켓의 실시간 및 역사적 데이터를 제공하는 API 세트입니다.
    15년 이상의 역사적 데이터와 전체 시장/거래량 커버리지를 제공합니다.

    지원하는 기능:
    - 실시간 옵션 데이터 (REALTIME_OPTIONS)
    - 역사적 옵션 데이터 (HISTORICAL_OPTIONS)
    - 그리스 및 내재가치 (IV) 지원
    - 옵션 체인 조회
    - 개별 옵션 계약 조회

    사용 예제:
        >>> client = AlphaVantageClient()
        >>> # 실시간 옵션 데이터
        >>> options = await client.options.realtime_options("AAPL")
        >>> # 역사적 옵션 데이터
        >>> history = await client.options.historical_options("AAPL", "2024-01-15")
    """

    async def realtime_options(
        self,
        symbol: str,
        require_greeks: Optional[bool] = None,
        contract: Optional[str] = None,
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        전체 시장 커버리지를 갖는 실시간 미국 옵션 데이터를 가져옵니다.

        이 API는 전체 시장 커버리지를 갖는 실시간 미국 옵션 데이터를 반환합니다.
        옵션 체인은 만료일 순으로 정렬되며, 동일 만료일 내에서는
        행사가격이 낮은 것부터 높은 순으로 정렬됩니다.

        Args:
            symbol: 주식 심보 (예: "IBM", "AAPL")
            require_greeks: 그리스 및 내재가치(IV) 필드 활성화 여부
                           기본값은 False이며, True로 설정시 그리스와 IV 포함
            contract: 미국 옵션 계약 ID
                     기본값은 설정하지 않으며, 전체 옵션 체인을 반환
            datatype: 출력 형식 ("json" 또는 "csv")

        Returns:
            dict: 실시간 옵션 데이터를 포함한 딕셔너리
                 - data: 옵션 체인 데이터
                 - meta_data: 메타데이터 (심볼, 마지막 업데이트 시간 등)

        각 옵션 데이터 항목:
            - contractID: 계약 ID
            - strike: 행사가격
            - type: 옵션 유형 (call/put)
            - expiration: 만료일
            - bid: 매수 호가
            - ask: 매도 호가
            - last: 마지막 거래가격
            - volume: 거래량
            - open_interest: 미결제약

        Example:
            >>> # IBM 실시간 옵션 데이터 (그리스 포함)
            >>> options = await client.options.realtime_options(
            ...     symbol="IBM",
            ...     require_greeks=True
            ... )
            >>> print(f"옵션 체인 개수: {len(options['data'])}")

            >>> # 특정 옵션 계약 조회
            >>> specific = await client.options.realtime_options(
            ...     symbol="AAPL",
            ...     contract="AAPL240119C00150000"
            ... )
        """
        params = {"function": "REALTIME_OPTIONS", "symbol": symbol}

        if require_greeks is not None:
            params["require_greeks"] = str(require_greeks).lower()
        if contract is not None:
            params["contract"] = contract
        if datatype != "json":
            params["datatype"] = datatype

        return await self.client._make_request(params)

    async def historical_options(
        self,
        symbol: str,
        date: str,
        require_greeks: Optional[bool] = None,
        contract: Optional[str] = None,
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        지정된 날짜의 역사적 미국 옵션 데이터를 가져옵니다.

        특정 거래일의 옵션 체인 스냅샷을 제공합니다.
        15년 이상의 역사적 데이터를 지원하며, 과거 옵션 가격 및
        변동성 분석에 필요한 데이터를 제공합니다.

        Args:
            symbol: 주식 심보 (예: "IBM", "AAPL")
            date: 조회할 날짜 (YYYY-MM-DD 형식, 예: "2024-01-15")
            require_greeks: 그리스 및 내재가치(IV) 필드 활성화 여부
                           기본값은 False이며, True로 설정시 그리스와 IV 포함
            contract: 미국 옵션 계약 ID (특정 계약만 조회시 사용)
            datatype: 출력 형식 ("json" 또는 "csv")

        Returns:
            dict: 역사적 옵션 데이터를 포함한 딕셔너리
                 - data: 해당 날짜의 옵션 체인 데이터
                 - meta_data: 메타데이터 (심보, 날짜 등)

        각 옵션 데이터 항목:
            - contractID: 계약 ID
            - strike: 행사가격
            - type: 옵션 유형 (call/put)
            - expiration: 만료일
            - last: 마지막 거래가격
            - volume: 거래량
            - open_interest: 미결제약
            - change: 가격 변동
            - change_percentage: 변동률

        Example:
            >>> # 2024년 1월 15일 IBM 옵션 데이터
            >>> historical = await client.options.historical_options(
            ...     symbol="IBM",
            ...     date="2024-01-15",
            ...     require_greeks=True
            ... )
            >>> print(f"해당 날짜 옵션 개수: {len(historical['data'])}")

            >>> # 특정 계약의 역사적 데이터
            >>> contract_history = await client.options.historical_options(
            ...     symbol="AAPL",
            ...     date="2024-01-15",
            ...     contract="AAPL240119C00150000"
            ... )
        """
        params = {"function": "HISTORICAL_OPTIONS", "symbol": symbol}

        if date is not None:
            params["date"] = date
        if datatype != "json":
            params["datatype"] = datatype

        return await self.client._make_request(params)

    # Convenience methods for common use cases
    async def get_option_chain(
        self, symbol: str, with_greeks: bool = True
    ) -> dict[str, Any]:
        """
        Get complete realtime option chain with Greeks and implied volatility.

        Convenience method to get the full option chain for a symbol with
        Greeks and implied volatility data included.

        Args:
            symbol: The equity symbol
            with_greeks: Whether to include Greeks and IV data

        Returns:
            Dictionary containing complete option chain data
        """
        return await self.realtime_options(symbol=symbol, require_greeks=with_greeks)

    async def get_historical_chain(self, symbol: str, date: str) -> dict[str, Any]:
        """
        특정 날짜의 역사적 옵션 체인을 가져오는 편의 메서드입니다.

        historical_options 메서드의 단순화된 버전으로, 특정 날짜의
        전체 옵션 체인을 쉽게 조회할 수 있습니다.

        Args:
            symbol: 주식 심보 (예: "AAPL", "TSLA")
            date: 조회할 날짜 (YYYY-MM-DD 형식)

        Returns:
            dict: 해당 날짜의 옵션 체인 데이터

        Example:
            >>> # 2024년 1월 15일 애플 옵션 체인
            >>> historical_chain = await client.options.get_historical_chain(
            ...     symbol="AAPL",
            ...     date="2024-01-15"
            ... )
            >>> print(f"해당 날짜 옵션 개수: {len(historical_chain['data'])}")

            >>> # 해당 날짜의 콜/풀 비율 분석
            >>> calls = [opt for opt in historical_chain['data'] if opt['type'] == 'call']
            >>> puts = [opt for opt in historical_chain['data'] if opt['type'] == 'put']
            >>> call_put_ratio = len(calls) / len(puts)
            >>> print(f"Call/Put 비율: {call_put_ratio:.2f}")
        """
        return await self.historical_options(symbol=symbol, date=date)

    async def get_option_contract(
        self,
        symbol: str,
        contract: str,
        require_greeks: bool = True,
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        특정 옵션 계약의 데이터를 가져오는 편의 메서드입니다.

        개별 옵션 계약의 상세 정보를 조회할 때 사용합니다.
        기본적으로 그리스와 내재가치를 포함하여 상세한 분석이 가능합니다.

        Args:
            symbol: 주식 심보 (예: "AAPL")
            contract: 옵션 계약 ID (예: "AAPL240119C00150000")
            require_greeks: 그리스 및 IV 포함 여부 (기본값: True)
            datatype: 출력 형식 ("json" 또는 "csv")

        Returns:
            dict: 특정 옵션 계약의 데이터
                 - contractID: 계약 ID
                 - strike: 행사가격
                 - type: 옵션 유형 (call/put)
                 - bid/ask: 매수/매도 호가
                 - last: 마지막 거래가
                 - delta, gamma, theta, vega: 그리스 값들
                 - implied_volatility: 내재가치

        Example:
            >>> # 애플 2024년 1월 19일 만료 150달러 콜 옵션
            >>> contract_data = await client.options.get_option_contract(
            ...     symbol="AAPL",
            ...     contract="AAPL240119C00150000"
            ... )
            >>> print(f"델타: {contract_data['delta']}")
            >>> print(f"감마: {contract_data['gamma']}")
            >>> print(f"내재가치: {contract_data['implied_volatility']}")
        """
        return await self.realtime_options(
            symbol=symbol,
            contract=contract,
            require_greeks=require_greeks,
            datatype=datatype,
        )
