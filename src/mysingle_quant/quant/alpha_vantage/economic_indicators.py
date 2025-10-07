"""
Alpha Vantage API 클라이언트 - 경제지표 모듈

미국의 주요 경제지표 데이터를 제공하여 투자 전략 수립과
애플리케이션 개발에 활용할 수 있습니다.

지원하는 경제지표 API:
- REAL_GDP: 실질 국내총생산
- REAL_GDP_PER_CAPITA: 실질 1인당 GDP
- TREASURY_YIELD: 국채 수익률
- FEDERAL_FUNDS_RATE: 연방기금금리
- CPI: 소비자물가지수
- INFLATION: 인플레이션
- RETAIL_SALES: 소매판매
- DURABLES: 내구재 주문
- UNEMPLOYMENT: 실업률
- NONFARM_PAYROLL: 비농업 고용
"""

from typing import Any, Literal

from .base import BaseAPIHandler


class EconomicIndicators(BaseAPIHandler):
    """
    Alpha Vantage 경제지표 API 핸들러입니다.

    미국의 주요 경제지표에 대한 접근을 제공하며, 투자 전략 수립과
    애플리케이션 개발에 자주 사용되는 핵심 경제 데이터를 제공합니다.

    주요 기능:
    - 거시경제 지표 조회 (GDP, 인플레이션, 실업률 등)
    - 통화정책 지표 모니터링 (연방기금금리, 국채수익률)
    - 소비 및 산업 지표 추적 (소매판매, 내구재 주문)
    - 고용 시장 데이터 분석 (비농업 고용, 실업률)
    """

    async def real_gdp(
        self,
        interval: Literal["quarterly", "annual"] = "annual",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        미국의 연간 및 분기별 실질 GDP 데이터를 조회합니다.

        실질 국내총생산(Real GDP)은 인플레이션을 조정한 경제 성장률을 나타내며,
        경제 성장 분석과 투자 전략 수립의 핵심 지표입니다.

        Args:
            interval (str, optional): 데이터 주기. 기본값은 'annual'
                                     - 'quarterly': 분기별 데이터
                                     - 'annual': 연간 데이터
            datatype (str, optional): 응답 형식. 기본값은 'json'
                                     - 'json': JSON 형식
                                     - 'csv': CSV 형식

        Returns:
            dict: 실질 GDP 시계열 데이터
                - 'name': 지표명
                - 'interval': 데이터 주기
                - 'unit': 데이터 단위 (수십억 달러)
                - 'data': 시계열 데이터 리스트
                  각 항목: {'date': '날짜', 'value': 'GDP 값'}

        Example:
            >>> economic_client = EconomicIndicators(api_key="your_api_key")
            >>> # 연간 실질 GDP 데이터
            >>> annual_gdp = await economic_client.real_gdp()
            >>> print(f"최신 GDP: {annual_gdp['data'][0]['value']}")
            >>>
            >>> # 분기별 실질 GDP로 경기 사이클 분석
            >>> quarterly_gdp = await economic_client.real_gdp(interval="quarterly")
            >>> recent_quarters = quarterly_gdp['data'][:4]
            >>> for quarter in recent_quarters:
            >>>     print(f"{quarter['date']}: {quarter['value']}B")
        """
        params = {"function": "REAL_GDP", "interval": interval, "datatype": datatype}
        return await self.client._make_request(params)

    async def real_gdp_per_capita(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        미국의 분기별 실질 1인당 GDP 데이터를 조회합니다.

        실질 1인당 GDP는 인플레이션을 조정한 인구 1인당 경제 성과를 나타내며,
        생활수준 향상과 경제 발전 정도를 측정하는 핵심 지표입니다.

        Args:
            datatype (str, optional): 응답 형식. 기본값은 'json'
                                     - 'json': JSON 형식
                                     - 'csv': CSV 형식

        Returns:
            dict: 실질 1인당 GDP 시계열 데이터
                - 'name': 지표명 ('Real gross domestic product per capita')
                - 'interval': '분기별' (Quarterly)
                - 'unit': '달러'
                - 'data': 시계열 데이터 리스트
                  각 항목: {'date': '날짜', 'value': '1인당 GDP 값'}

        Example:
            >>> economic_client = EconomicIndicators(api_key="your_api_key")
            >>> # 실질 1인당 GDP 데이터로 생활수준 분석
            >>> gdp_per_capita = await economic_client.real_gdp_per_capita()
            >>> print(f"최신 1인당 GDP: ${gdp_per_capita['data'][0]['value']}")
            >>>
            >>> # 최근 5년간 1인당 GDP 성장률 계산
            >>> recent_data = gdp_per_capita['data'][:20]  # 5년 분기 데이터
            >>> current = float(recent_data[0]['value'])
            >>> five_years_ago = float(recent_data[-1]['value'])
            >>> growth_rate = (current / five_years_ago - 1) * 100
            >>> print(f"5년간 성장률: {growth_rate:.2f}%")
        """
        params = {"function": "REAL_GDP_PER_CAPITA", "datatype": datatype}
        return await self.client._make_request(params)

    async def treasury_yield(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
        maturity: Literal[
            "3month", "2year", "5year", "7year", "10year", "30year"
        ] = "10year",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        주어진 만기의 미국 국채 수익률 데이터를 조회합니다.

        국채 수익률은 금리 변화, 통화정책 방향성, 경제 전망을 파악하는 핵심 지표로
        채권 투자, 주식 시장 분석, 거시경제 전망에 필수적인 데이터입니다.

        Args:
            interval (str, optional): 데이터 주기. 기본값은 'monthly'
                                     - 'daily': 일일 데이터
                                     - 'weekly': 주간 데이터
                                     - 'monthly': 월간 데이터
            maturity (str, optional): 국채 만기. 기본값은 '10year'
                                     - '3month': 3개월 국채
                                     - '2year': 2년 국채
                                     - '5year': 5년 국채
                                     - '7year': 7년 국채
                                     - '10year': 10년 국채 (벤치마크)
                                     - '30year': 30년 국채
            datatype (str, optional): 응답 형식. 기본값은 'json'
                                     - 'json': JSON 형식
                                     - 'csv': CSV 형식

        Returns:
            dict: 국채 수익률 시계열 데이터
                - 'name': 지표명
                - 'interval': 데이터 주기
                - 'unit': 단위 (퍼센트)
                - 'data': 시계열 데이터 리스트
                  각 항목: {'date': '날짜', 'value': '수익률(%)'}

        Example:
            >>> economic_client = EconomicIndicators(api_key="your_api_key")
            >>> # 10년 국채 월간 수익률 (기본값)
            >>> ten_year = await economic_client.treasury_yield()
            >>> print(f"현재 10년 국채 수익률: {ten_year['data'][0]['value']}%")
            >>>
            >>> # 2년 국채 주간 수익률로 단기 금리 추세 분석
            >>> two_year = await economic_client.treasury_yield(
            ...     maturity="2year",
            ...     interval="weekly"
            ... )
            >>>
            >>> # 수익률 곡선 분석을 위한 다양한 만기 비교
            >>> long_term = await economic_client.treasury_yield(maturity="30year")
            >>> short_term = await economic_client.treasury_yield(maturity="3month")
            >>> spread = float(long_term['data'][0]['value']) - float(short_term['data'][0]['value'])
            >>> print(f"장단기 금리차: {spread:.2f}%")
        """
        params = {
            "function": "TREASURY_YIELD",
            "interval": interval,
            "maturity": maturity,
            "datatype": datatype,
        }
        return await self.client._make_request(params)

    async def federal_funds_rate(
        self,
        interval: Literal["daily", "weekly", "monthly"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        미국의 일일, 주간, 월간 연방기금금리 데이터를 조회합니다.

        연방기금금리은 예금기관들이 서로 지급준비금을 거래할 때 사용하는 금리로,
        미국 통화정책의 핵심 지표이며 전 세계 금융시장에 영향을 미칩니다.

        Args:
            interval (str, optional): 데이터 주기. 기본값은 'monthly'
                                     - 'daily': 일일 데이터
                                     - 'weekly': 주간 데이터
                                     - 'monthly': 월간 데이터
            datatype (str, optional): 응답 형식. 기본값은 'json'
                                     - 'json': JSON 형식
                                     - 'csv': CSV 형식

        Returns:
            dict: 연방기금금리 시계열 데이터
                - 'name': 지표명 ('Federal Funds Rate')
                - 'interval': 데이터 주기
                - 'unit': 단위 (퍼센트)
                - 'data': 시계열 데이터 리스트
                  각 항목: {'date': '날짜', 'value': '금리(%)'}

        Example:
            >>> economic_client = EconomicIndicators(api_key="your_api_key")
            >>> # 연방기금금리 월간 데이터
            >>> fed_rate = await economic_client.federal_funds_rate()
            >>> print(f"현재 연방기금금리: {fed_rate['data'][0]['value']}%")
            >>>
            >>> # 주간 데이터로 통화정책 변화 추세 분석
            >>> weekly_fed = await economic_client.federal_funds_rate(interval="weekly")
            >>> recent_weeks = weekly_fed['data'][:8]
            >>> for week in recent_weeks:
            >>>     print(f"{week['date']}: {week['value']}%")
        """
        params = {
            "function": "FEDERAL_FUNDS_RATE",
            "interval": interval,
            "datatype": datatype,
        }
        return await self.client._make_request(params)

    async def cpi(
        self,
        interval: Literal["monthly", "semiannual"] = "monthly",
        datatype: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        """
        미국의 월간 및 반기별 소비자물가지수(CPI) 데이터를 조회합니다.

        CPI는 경제 전반의 인플레이션 수준을 측정하는 대표적인 지표로,
        도시 소비자를 대상으로 한 전체 소비자물가지수를 제공합니다.

        Args:
            interval (str, optional): 데이터 주기. 기본값은 'monthly'
                                     - 'monthly': 월간 데이터
                                     - 'semiannual': 반기별 데이터
            datatype (str, optional): 응답 형식. 기본값은 'json'
                                     - 'json': JSON 형식
                                     - 'csv': CSV 형식

        Returns:
            dict: CPI 시계열 데이터
                - 'name': 지표명 ('Consumer Price Index')
                - 'interval': 데이터 주기
                - 'unit': 단위 (지수)
                - 'data': 시계열 데이터 리스트
                  각 항목: {'date': '날짜', 'value': 'CPI 지수'}

        Example:
            >>> economic_client = EconomicIndicators(api_key="your_api_key")
            >>> # 월간 CPI 데이터로 인플레이션 추세 분석
            >>> monthly_cpi = await economic_client.cpi()
            >>> print(f"최신 CPI: {monthly_cpi['data'][0]['value']}")
            >>>
            >>> # 전년 대비 CPI 상승률 계산
            >>> current_cpi = float(monthly_cpi['data'][0]['value'])
            >>> year_ago_cpi = float(monthly_cpi['data'][12]['value'])
            >>> inflation_rate = (current_cpi / year_ago_cpi - 1) * 100
            >>> print(f"전년 대비 인플레이션: {inflation_rate:.2f}%")
        """
        params = {"function": "CPI", "interval": interval, "datatype": datatype}
        return await self.client._make_request(params)

    async def inflation(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        미국의 연간 인플레이션율(소비자물가 기준) 데이터를 조회합니다.

        소비자물가를 기준으로 한 연간 인플레이션율을 제공하며,
        시간에 따른 물가 상승률을 측정하여 경제 안정성과 통화정책 효과를 평가합니다.

        Args:
            datatype (str, optional): 응답 형식. 기본값은 'json'
                                     - 'json': JSON 형식
                                     - 'csv': CSV 형식

        Returns:
            dict: 인플레이션율 시계열 데이터
                - 'name': 지표명 ('Inflation - Consumer Prices')
                - 'interval': 'Annual' (연간)
                - 'unit': '퍼센트'
                - 'data': 시계열 데이터 리스트
                  각 항목: {'date': '년도', 'value': '인플레이션율(%)'}

        Example:
            >>> economic_client = EconomicIndicators(api_key="your_api_key")
            >>> # 연간 인플레이션율 데이터
            >>> inflation_data = await economic_client.inflation()
            >>> print(f"최신 인플레이션율: {inflation_data['data'][0]['value']}%")
        """
        params = {"function": "INFLATION", "datatype": datatype}
        return await self.client._make_request(params)

    async def retail_sales(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        미국의 월간 선행 소매판매 데이터를 조회합니다.

        소매판매 데이터는 소매점의 총 매출을 측정하여
        소비자 지출 패턴과 경제 활동 수준에 대한 통찰력을 제공합니다.

        Args:
            datatype (str, optional): 응답 형식. 기본값은 'json'
                                     - 'json': JSON 형식
                                     - 'csv': CSV 형식

        Returns:
            dict: 소매판매 시계열 데이터
                - 'name': 지표명 ('Advance Retail Sales: Retail Trade')
                - 'interval': 'Monthly' (월간)
                - 'unit': '수백만 달러'
                - 'data': 시계열 데이터 리스트
                  각 항목: {'date': '날짜', 'value': '소매판매액'}

        Example:
            >>> economic_client = EconomicIndicators(api_key="your_api_key")
            >>> # 월간 소매판매 데이터로 소비 트렌드 분석
            >>> retail_data = await economic_client.retail_sales()
            >>> print(f"최신 소매판매: ${retail_data['data'][0]['value']}M")
        """
        params = {"function": "RETAIL_SALES", "datatype": datatype}
        return await self.client._make_request(params)

    async def durables(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the monthly manufacturers' new orders of durable goods in the United States.

        Durable goods are products that are expected to last for at least three years.
        This indicator provides insights into manufacturing activity and business investment.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Durable goods orders time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.durables()
        """
        params = {"function": "DURABLES", "datatype": datatype}
        return await self.client._make_request(params)

    async def unemployment(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the monthly unemployment data of the United States.

        The unemployment rate represents the number of unemployed as a percentage
        of the labor force. This is a key indicator of economic health.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Unemployment rate time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.unemployment()
        """
        params = {"function": "UNEMPLOYMENT", "datatype": datatype}
        return await self.client._make_request(params)

    async def nonfarm_payroll(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get the monthly US All Employees: Total Nonfarm (commonly known as Total Nonfarm Payroll).

        This measures the number of U.S. workers in the economy that excludes proprietors,
        private household employees, unpaid volunteers, farm employees, and
        the unincorporated self-employed.

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Nonfarm payroll time series data

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> data = await client.economic_indicators.nonfarm_payroll()
        """
        params = {"function": "NONFARM_PAYROLL", "datatype": datatype}
        return await self.client._make_request(params)

    # Convenience methods for common use cases
    async def get_key_indicators(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get a collection of key economic indicators in a single call.

        This convenience method fetches multiple key economic indicators:
        - Real GDP (annual)
        - Treasury Yield (10-year, monthly)
        - Federal Funds Rate (monthly)
        - CPI (monthly)
        - Unemployment Rate

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Dictionary containing multiple economic indicators

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> indicators = await client.economic_indicators.get_key_indicators()
        """
        import asyncio

        # Fetch multiple indicators concurrently
        tasks = [
            self.real_gdp(datatype=datatype),
            self.treasury_yield(datatype=datatype),
            self.federal_funds_rate(datatype=datatype),
            self.cpi(datatype=datatype),
            self.unemployment(datatype=datatype),
        ]

        results = await asyncio.gather(*tasks)

        return {
            "real_gdp": results[0],
            "treasury_yield_10y": results[1],
            "federal_funds_rate": results[2],
            "cpi": results[3],
            "unemployment": results[4],
        }

    async def get_monetary_policy_indicators(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get monetary policy related indicators.

        This convenience method fetches indicators related to monetary policy:
        - Federal Funds Rate
        - Treasury Yield (10-year)
        - Inflation

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Dictionary containing monetary policy indicators

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> indicators = await client.economic_indicators.get_monetary_policy_indicators()
        """
        import asyncio

        tasks = [
            self.federal_funds_rate(datatype=datatype),
            self.treasury_yield(datatype=datatype),
            self.inflation(datatype=datatype),
        ]

        results = await asyncio.gather(*tasks)

        return {
            "federal_funds_rate": results[0],
            "treasury_yield_10y": results[1],
            "inflation": results[2],
        }

    async def get_economic_growth_indicators(
        self, datatype: Literal["json", "csv"] = "json"
    ) -> dict[str, Any]:
        """
        Get economic growth related indicators.

        This convenience method fetches indicators related to economic growth:
        - Real GDP (annual)
        - Real GDP per Capita
        - Retail Sales
        - Durable Goods Orders
        - Nonfarm Payroll

        Args:
            datatype: Response format. Options: "json", "csv"

        Returns:
            Dictionary containing economic growth indicators

        Example:
            >>> client = AlphaVantageClient(api_key="your_key")
            >>> indicators = await client.economic_indicators.get_economic_growth_indicators()
        """
        import asyncio

        tasks = [
            self.real_gdp(datatype=datatype),
            self.real_gdp_per_capita(datatype=datatype),
            self.retail_sales(datatype=datatype),
            self.durables(datatype=datatype),
            self.nonfarm_payroll(datatype=datatype),
        ]

        results = await asyncio.gather(*tasks)

        return {
            "real_gdp": results[0],
            "real_gdp_per_capita": results[1],
            "retail_sales": results[2],
            "durable_goods": results[3],
            "nonfarm_payroll": results[4],
        }
