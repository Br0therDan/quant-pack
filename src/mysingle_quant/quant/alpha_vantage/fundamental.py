"""
Alpha Vantage API 클라이언트 - 기본 데이터 모듈

기업의 기본적인 재무 데이터에 대한 접근을 제공합니다.
손익계산서, 대차대조표, 현금흐름표 등의 재무제표와
배당, 주식 분할, 실적 등의 정보를 제공합니다.

지원하는 기능:
- 기업 개요 정보
- ETF 프로필 및 보유 종목
- 재무제표 (손익계산서, 대차대조표, 현금흐름표)
- 배당 및 주식 분할 이벤트
- 실적 및 예상 실적
- 상장 및 상장폐지 상태
- 실적 발표 캘린더
"""

import logging
from typing import TYPE_CHECKING, Any, Literal, Optional

from .base import BaseAPIHandler

if TYPE_CHECKING:
    pass  # Remove circular import reference

logger = logging.getLogger(__name__)


class Fundamental(BaseAPIHandler):
    """
    기본 데이터 API 핸들러

    Alpha Vantage의 기본 데이터 API에 대한 인터페이스를 제공합니다.
    다양한 시간 차원에서 핵심 재무 메트릭, 손익계산서,
    대차대조표, 현금흐름 및 기타 기본 데이터 포인트를 제공합니다.

    지원하는 API 기능:
    - OVERVIEW: 기업 개요 정보
    - ETF_PROFILE: ETF 프로필 및 보유 종목
    - DIVIDENDS: 배당 이벤트
    - SPLITS: 주식 분할 이벤트
    - INCOME_STATEMENT: 손익계산서
    - BALANCE_SHEET: 대차대조표
    - CASH_FLOW: 현금흐름표
    - SHARES_OUTSTANDING: 유통 주식 수
    - EARNINGS: 실적 데이터
    - EARNINGS_ESTIMATES: 예상 실적
    - LISTING_STATUS: 상장/상장폐지 상태
    - EARNINGS_CALENDAR: 실적 발표 캘린더
    - IPO_CALENDAR: IPO 캘린더

    사용 예제:
        >>> client = AlphaVantageClient()
        >>> # 기업 개요 정보 조회
        >>> overview = await client.fundamental.company_overview("AAPL")
        >>> # 손익계산서 조회
        >>> income = await client.fundamental.income_statement("AAPL")
    """

    async def _call_fundamental_api(
        self,
        function: str,
        symbol: Optional[str] = None,
        horizon: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        기본 데이터 API 호출을 위한 기본 메서드

        Args:
            function: API 함수 이름
            symbol: 주식 심볼 (e.g., "AAPL")
            horizon: 예상 실적 기간 (EARNINGS_ESTIMATES용)
            **kwargs: 추가 파라미터

        Returns:
            API 응답 데이터 (리스트 또는 딕셔너리)

        Raises:
            ValueError: 필수 파라미터가 빠진 경우
        """

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
        """
        기본 데이터 API 응답을 함수 타입에 따라 파싱합니다

        Args:
            data: API 원시 응답 데이터
            function: API 함수 이름
            symbol: 주식 심볼

        Returns:
            파싱된 데이터 (리스트 또는 딕셔너리)
        """

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
        """
        기업 개요 정보를 가져옵니다.

        상장 기업의 기본 정보, 재무 지표, 시가총액, 전체적인
        비즈니스 개요 등을 제공합니다. 투자 결정을 내리기 전에
        필수적으로 확인해야 할 핵심 정보들을 제공합니다.

        Args:
            symbol: 기업 주식 심볼 (예: "AAPL", "MSFT")

        Returns:
            dict: 기업 개요 정보를 포함한 딕셔너리
                 - symbol: 주식 심볼
                 - name: 회사명
                 - description: 비즈니스 설명
                 - sector: 업종
                 - industry: 산업
                 - market_capitalization: 시가총액
                 - pe_ratio: 주가수익비율
                 - dividend_yield: 배당수익률
                 - book_value: 주당 순자산가치

        Example:
            >>> # 애플 기업 개요 조회
            >>> overview = await client.fundamental.overview("AAPL")
            >>> print(f"회사명: {overview['name']}")
            >>> print(f"시가총액: {overview['market_capitalization']}")
            >>> print(f"PE 비율: {overview['pe_ratio']}")
        """
        result = await self._call_fundamental_api("OVERVIEW", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def etf_profile(self, symbol: str) -> dict[str, Any]:
        """
        ETF(상장지수펀드) 프로필 정보를 가져옵니다.

        ETF의 기본 정보, 투자 목표, 분배 전략, 수수료,
        기초 자산의 구성 비율 등 ETF 투자에 필요한
        모든 정보를 제공합니다.

        Args:
            symbol: ETF 심볼 (예: "SPY", "QQQ")

        Returns:
            dict: ETF 프로필 정보를 포함한 딕셔너리
                 - symbol: ETF 심볼
                 - name: ETF 이름
                 - description: 투자 목표 및 전략
                 - expense_ratio: 비용 비율
                 - dividend_yield: 배당 수익률
                 - holdings: 주요 보유 종목
                 - sectors: 섹터별 분배 비율

        Example:
            >>> # S&P 500 ETF 프로필 조회
            >>> spy_profile = await client.fundamental.etf_profile("SPY")
            >>> print(f"ETF 이름: {spy_profile['name']}")
            >>> print(f"비용 비율: {spy_profile['expense_ratio']}")
            >>> print(f"배당 수익률: {spy_profile['dividend_yield']}")
        """
        result = await self._call_fundamental_api("ETF_PROFILE", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def dividends(self, symbol: str) -> list[dict[str, Any]]:
        """
        배당금 지급 이력을 가져옵니다.

        과거부터 현재까지의 모든 배당금 지급 내역을 제공합니다.
        배당금 지급일, 배당률, 배당 수익률 등의 정보를 통해
        배당 투자 전략 수립에 필요한 데이터를 제공합니다.

        Args:
            symbol: 주식 심볼 (예: "AAPL", "KO")

        Returns:
            list: 배당금 지급 이력 리스트
                  각 항목은 다음을 포함:
                  - ex_dividend_date: 배당락일
                  - dividend_amount: 배당금액
                  - record_date: 배당기준일
                  - payment_date: 배당지급일
                  - declaration_date: 배당선언일

        Example:
            >>> # 코카콜라 배당 이력 조회
            >>> dividends = await client.fundamental.dividends("KO")
            >>> for dividend in dividends[:5]:  # 최근 5개 조회
            ...     print(f"날짜: {dividend['ex_dividend_date']}, 금액: {dividend['dividend_amount']}")
        """
        result = await self._call_fundamental_api("DIVIDENDS", symbol=symbol)
        return result if isinstance(result, list) else []

    async def splits(self, symbol: str) -> list[dict[str, Any]]:
        """
        주식 분할 이력을 가져옵니다.

        과거부터 현재까지의 모든 주식 분할 내역을 제공합니다.
        주식 분할 비율, 분할 실행일 등의 정보를 통해
        주가 및 주식 수량 변화를 추적할 수 있습니다.

        Args:
            symbol: 주식 심볼 (예: "AAPL", "TSLA")

        Returns:
            list: 주식 분할 이력 리스트
                  각 항목은 다음을 포함:
                  - date: 분할 실행일
                  - split_coefficient: 분할 계수 (예: 2:1 분할의 경우 0.5)
                  - from_factor: 분할 전 주식 수
                  - to_factor: 분할 후 주식 수

        Example:
            >>> # 애플 주식 분할 이력 조회
            >>> splits = await client.fundamental.splits("AAPL")
            >>> for split in splits:
            ...     print(f"날짜: {split['date']}, 비율: {split['from_factor']}:{split['to_factor']}")
        """
        result = await self._call_fundamental_api("SPLITS", symbol=symbol)
        return result if isinstance(result, list) else []

    async def income_statement(self, symbol: str) -> dict[str, Any]:
        """
        손익계산서 데이터를 가져옵니다.

        기업의 매출, 운영비용, 순이익 등 수익성 분석에 필요한
        핵심 재무 정보를 제공합니다. 연도별 및 분기별 손익계산서
        데이터를 통해 기업의 성장성과 수익성을 평가할 수 있습니다.

        Args:
            symbol: 주식 심보 (예: "AAPL", "MSFT")

        Returns:
            dict: 손익계산서 데이터를 포함한 딕셔너리
                 - symbol: 주식 심보
                 - annual_reports: 연도별 손익계산서
                 - quarterly_reports: 분기별 손익계산서

        각 보고서 항목:
            - fiscal_date_ending: 회계년도 종료일
            - reported_date: 보고서 발표일
            - total_revenue: 총 매출
            - gross_profit: 매출총이익
            - operating_income: 영업이익
            - net_income: 순이익

        Example:
            >>> # 애플 손익계산서 조회
            >>> income = await client.fundamental.income_statement("AAPL")
            >>> annual_reports = income['annual_reports']
            >>> latest = annual_reports[0]  # 최신 연도 보고서
            >>> print(f"매출: {latest['total_revenue']}")
            >>> print(f"순이익: {latest['net_income']}")
        """
        result = await self._call_fundamental_api("INCOME_STATEMENT", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def balance_sheet(self, symbol: str) -> dict[str, Any]:
        """
        대차대조표 데이터를 가져옵니다.

        기업의 자산, 부채, 자본 구성을 보여주는 대차대조표
        데이터를 제공합니다. 기업의 재무 안정성과 유동성을
        평가하는 데 필수적인 정보를 제공합니다.

        Args:
            symbol: 주식 심보 (예: "AAPL", "MSFT")

        Returns:
            dict: 대차대조표 데이터를 포함한 딕셔너리
                 - symbol: 주식 심보
                 - annual_reports: 연도별 대차대조표
                 - quarterly_reports: 분기별 대차대조표

        각 보고서 항목:
            - fiscal_date_ending: 회계년도 종료일
            - reported_date: 보고서 발표일
            - total_assets: 총 자산
            - total_current_assets: 유동 자산
            - total_liabilities: 총 부채
            - total_shareholder_equity: 주주 지분

        Example:
            >>> # 애플 대차대조표 조회
            >>> balance = await client.fundamental.balance_sheet("AAPL")
            >>> annual_reports = balance['annual_reports']
            >>> latest = annual_reports[0]  # 최신 연도 보고서
            >>> print(f"총 자산: {latest['total_assets']}")
            >>> print(f"주주 지분: {latest['total_shareholder_equity']}")
        """
        result = await self._call_fundamental_api("BALANCE_SHEET", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def cash_flow(self, symbol: str) -> dict[str, Any]:
        """
        현금흐름표 데이터를 가져옵니다.

        기업의 영업, 투자, 재무 활동에서 발생한 현금흐름을
        제공합니다. 기업의 현금 창출 능력과 유동성 상태를
        평가하는 데 필수적인 정보를 제공합니다.

        Args:
            symbol: 주식 심보 (예: "AAPL", "MSFT")

        Returns:
            dict: 현금흐름표 데이터를 포함한 딕셔너리
                 - symbol: 주식 심보
                 - annual_reports: 연도별 현금흐름표
                 - quarterly_reports: 분기별 현금흐름표

        각 보고서 항목:
            - fiscal_date_ending: 회계년도 종료일
            - reported_date: 보고서 발표일
            - operating_cashflow: 영업 활동 현금흐름
            - capital_expenditures: 자본 지출
            - dividend_payout: 배당금 지급
            - free_cash_flow: 자유 현금흐름

        Example:
            >>> # 애플 현금흐름표 조회
            >>> cashflow = await client.fundamental.cash_flow("AAPL")
            >>> annual_reports = cashflow['annual_reports']
            >>> latest = annual_reports[0]  # 최신 연도 보고서
            >>> print(f"영업 현금흐름: {latest['operating_cashflow']}")
            >>> print(f"자유 현금흐름: {latest['free_cash_flow']}")
        """
        result = await self._call_fundamental_api("CASH_FLOW", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def shares_outstanding(self, symbol: str) -> list[dict[str, Any]]:
        """
        발행 주식 수 데이터를 가져옵니다.

        시간에 따른 발행 주식 수의 변화를 제공합니다.
        주식 분할, 자사주 매입, 신주 발행 등으로 인한
        발행 주식 수 변화를 추적할 수 있습니다.

        Args:
            symbol: 주식 심보 (예: "AAPL", "MSFT")

        Returns:
            list: 발행 주식 수 데이터 리스트
                  각 항목은 다음을 포함:
                  - date: 기준일
                  - shares_outstanding: 발행 주식 수
                  - shares_float: 유통 주식 수

        Example:
            >>> # 애플 발행 주식 수 조회
            >>> shares = await client.fundamental.shares_outstanding("AAPL")
            >>> for share_data in shares[:5]:  # 최근 5개 데이터
            ...     print(f"날짜: {share_data['date']}, 발행주식: {share_data['shares_outstanding']}")
        """
        result = await self._call_fundamental_api("SHARES_OUTSTANDING", symbol=symbol)
        return result if isinstance(result, list) else []

    async def earnings(self, symbol: str) -> dict[str, Any]:
        """
        실적 발표 데이터를 가져옵니다.

        과거부터 현재까지의 연도별 및 분기별 실제 실적 데이터와
        예상 실적 데이터를 제공합니다. 주당 순이익(EPS) 정보를
        통해 기업의 수익성 변화를 막대도형으로 확인할 수 있습니다.

        Args:
            symbol: 주식 심보 (예: "AAPL", "MSFT")

        Returns:
            dict: 실적 데이터를 포함한 딕셔너리
                 - symbol: 주식 심보
                 - annual_earnings: 연도별 실적
                 - quarterly_earnings: 분기별 실적

        각 실적 항목:
            - fiscal_date_ending: 회계년도 종료일
            - reported_date: 실적 발표일
            - reported_eps: 실제 주당 순이익
            - estimated_eps: 예상 주당 순이익
            - surprise: 예상 대비 실제 차이
            - surprise_percentage: 예상 대비 실제 차이 비율

        Example:
            >>> # 애플 실적 데이터 조회
            >>> earnings = await client.fundamental.earnings("AAPL")
            >>> quarterly = earnings['quarterly_earnings']
            >>> latest = quarterly[0]  # 최신 분기 실적
            >>> print(f"실제 EPS: {latest['reported_eps']}")
            >>> print(f"예상 EPS: {latest['estimated_eps']}")
            >>> print(f"서프라이즈: {latest['surprise_percentage']}%")
        """
        result = await self._call_fundamental_api("EARNINGS", symbol=symbol)
        return result if isinstance(result, dict) else {}

    async def earnings_estimates(
        self, symbol: str, horizon: Literal["3month", "6month", "12month"]
    ) -> dict[str, Any]:
        """
        애널리스트 실적 예상 데이터를 가져옵니다.

        주요 증권사 애널리스트들의 실적 예상 컨센서스를 제공합니다.
        미래 실적 예상치와 예상 범위를 통해 투자 결정에
        필요한 정보를 제공합니다.

        Args:
            symbol: 주식 심보 (예: "AAPL", "MSFT")
            horizon: 예상 기간 ("3month", "6month", "12month")

        Returns:
            dict: 실적 예상 데이터를 포함한 딕셔너리
                 - symbol: 주식 심보
                 - period: 예상 기간
                 - estimates: 애널리스트 예상 데이터

        예상 데이터 항목:
            - mean_estimate: 평균 예상치
            - median_estimate: 중간 예상치
            - high_estimate: 최고 예상치
            - low_estimate: 최저 예상치
            - number_of_estimates: 예상치 개수
            - standard_deviation: 표준편차

        Example:
            >>> # 애플 12개월 실적 예상 조회
            >>> estimates = await client.fundamental.earnings_estimates(
            ...     symbol="AAPL",
            ...     horizon="12month"
            ... )
            >>> print(f"평균 예상치: {estimates['mean_estimate']}")
            >>> print(f"예상 범위: {estimates['low_estimate']} ~ {estimates['high_estimate']}")
        """
        result = await self._call_fundamental_api(
            "EARNINGS_ESTIMATES", symbol=symbol, horizon=horizon
        )
        return result if isinstance(result, dict) else {}

    async def listing_status(self) -> list[dict[str, Any]]:
        """
        미국 주식 시장 상장 종목 목록을 가져옵니다.

        현재 미국 주식 시장에 상장된 모든 종목의 기본 정보를
        제공합니다. 종목 선별, 시장 분석, 포트폴리오 구성 등에
        필요한 기초 데이터를 제공합니다.

        Returns:
            list: 상장 종목 리스트
                  각 항목은 다음을 포함:
                  - symbol: 주식 심보
                  - name: 회사명
                  - exchange: 거래소
                  - asset_type: 자산 유형
                  - ipo_date: 상장일
                  - delisting_date: 상장 폐지일 (해당시)
                  - status: 상장 상태

        Example:
            >>> # 전체 상장 종목 조회
            >>> all_stocks = await client.fundamental.listing_status()
            >>> active_stocks = [s for s in all_stocks if s['status'] == 'Active']
            >>> print(f"전체 상장 종목 수: {len(all_stocks)}")
            >>> print(f"활성 상장 종목 수: {len(active_stocks)}")
        """
        result = await self._call_fundamental_api("LISTING_STATUS")
        return result if isinstance(result, list) else []

    async def earnings_calendar(self) -> list[dict[str, Any]]:
        """
        실적 발표 일정을 가져옵니다.

        향후 3개월간의 실적 발표 예정 일정을 제공합니다.
        투자자들이 실적 발표에 따른 주가 변동에 대비할 수 있도록
        주요 기업들의 실적 발표 일정을 제공합니다.

        Returns:
            list: 실적 발표 일정 리스트
                  각 항목은 다음을 포함:
                  - symbol: 주식 심보
                  - name: 회사명
                  - report_date: 실적 발표일
                  - fiscal_date_ending: 회계년도 종료일
                  - estimate: 예상 EPS
                  - currency: 통화

        Example:
            >>> # 향후 실적 발표 일정 조회
            >>> calendar = await client.fundamental.earnings_calendar()
            >>> for earning in calendar[:10]:  # 가장 빠른 10개
            ...     print(f"{earning['symbol']}: {earning['report_date']} - {earning['estimate']}")
        """
        result = await self._call_fundamental_api("EARNINGS_CALENDAR")
        return result if isinstance(result, list) else []

    async def ipo_calendar(self) -> list[dict[str, Any]]:
        """
        IPO(신규 상장) 일정을 가져옵니다.

        향후 예정된 신규 주식 상장 일정과 관련 정보를 제공합니다.
        새로운 투자 기회를 발굴하고 IPO 투자 전략을 수립하는 데
        필요한 정보를 제공합니다.

        Returns:
            list: IPO 일정 리스트
                  각 항목은 다음을 포함:
                  - symbol: 주식 심보
                  - name: 회사명
                  - ipo_date: 상장 예정일
                  - price_range_low: 최저 공모가
                  - price_range_high: 최고 공모가
                  - currency: 통화
                  - exchange: 상장 예정 거래소

        Example:
            >>> # 향후 IPO 일정 조회
            >>> ipo_schedule = await client.fundamental.ipo_calendar()
            >>> for ipo in ipo_schedule:
            ...     print(f"{ipo['name']}: {ipo['ipo_date']} - ${ipo['price_range_low']}-${ipo['price_range_high']}")
        """
        result = await self._call_fundamental_api("IPO_CALENDAR")
        return result if isinstance(result, list) else []
