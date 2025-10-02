"""
통합 서비스 팩토리 - 서비스 간 의존성 관리
"""

import logging

from .backtest_service import BacktestService
from .database_manager import DatabaseManager
from .market_data_service import MarketDataService
from .strategy_service import StrategyService

logger = logging.getLogger(__name__)


class ServiceFactory:
    """서비스 팩토리 - 서비스 간 의존성 주입 관리"""

    _instance = None
    _market_data_service: MarketDataService | None = None
    _strategy_service: StrategyService | None = None
    _backtest_service: BacktestService | None = None
    _database_manager: DatabaseManager | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_database_manager(self) -> DatabaseManager:
        """DatabaseManager 인스턴스 반환 (DuckDB 캐시)"""
        if self._database_manager is None:
            self._database_manager = DatabaseManager()
            self._database_manager.connect()
            logger.info("Created DatabaseManager instance")
        return self._database_manager

    def get_market_data_service(self) -> MarketDataService:
        """MarketDataService 인스턴스 반환 (DuckDB 연동)"""
        if self._market_data_service is None:
            database_manager = self.get_database_manager()
            self._market_data_service = MarketDataService(database_manager)
            logger.info("Created MarketDataService instance with DuckDB")
        return self._market_data_service

    def get_strategy_service(self) -> StrategyService:
        """StrategyService 인스턴스 반환"""
        if self._strategy_service is None:
            self._strategy_service = StrategyService()
            logger.info("Created StrategyService instance")
        return self._strategy_service

    def get_backtest_service(self) -> BacktestService:
        """BacktestService 인스턴스 반환 (DuckDB 연동 의존성 주입)"""
        if self._backtest_service is None:
            market_data_service = self.get_market_data_service()
            strategy_service = self.get_strategy_service()
            database_manager = self.get_database_manager()

            self._backtest_service = BacktestService(
                market_data_service=market_data_service,
                strategy_service=strategy_service,
                database_manager=database_manager,
            )
            logger.info("Created BacktestService instance with DuckDB integration")
        return self._backtest_service

    async def cleanup(self):
        """모든 서비스 정리"""
        if self._market_data_service:
            await self._market_data_service.close()

        if self._database_manager:
            self._database_manager.close()
            self._database_manager = None

        # 다른 서비스들도 필요시 정리
        logger.info("Services cleaned up")


# 전역 팩토리 인스턴스
service_factory = ServiceFactory()
