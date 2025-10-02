"""
공통 데이터 모델 정의

이 모듈은 전체 시스템에서 사용되는 공통 데이터 모델을 정의합니다.
Pydantic을 사용하여 타입 안전성과 데이터 검증을 보장합니다.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class TimeInterval(str, Enum):
    """시간 간격 열거형"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    INTRADAY_1MIN = "1min"
    INTRADAY_5MIN = "5min"
    INTRADAY_15MIN = "15min"
    INTRADAY_30MIN = "30min"
    INTRADAY_60MIN = "60min"


class MarketData(BaseModel):
    """시장 데이터 모델"""

    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float | None = None

    class Config:
        from_attributes = True


class StrategyConfig(BaseModel):
    """전략 설정 모델"""

    name: str
    template: str
    symbol: str
    parameters: dict[str, Any]
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class BacktestResult(BaseModel):
    """백테스트 결과 모델"""

    backtest_id: str
    strategy_name: str
    symbol: str
    start_date: date
    end_date: date
    initial_capital: float
    final_value: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float | None = None
    max_drawdown: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


__all__ = [
    "TimeInterval",
    "MarketData",
    "StrategyConfig",
    "BacktestResult",
]
