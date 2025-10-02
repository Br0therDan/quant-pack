"""
통합 백테스트 실행 서비스 - 모든 서비스 연동
"""

import logging
from datetime import UTC, datetime
from typing import Any

import numpy as np
from app.models.backtest import (
    Backtest,
    BacktestExecution,
    BacktestResult,
    BacktestStatus,
    PerformanceMetrics,
    Trade,
    TradeType,
)
from app.models.strategy import StrategyType
from app.services.market_data_service import MarketDataService
from app.services.strategy_service import StrategyService
from beanie import PydanticObjectId

logger = logging.getLogger(__name__)


class IntegratedBacktestExecutor:
    """통합 백테스트 실행기 - 모든 서비스 연동"""

    def __init__(
        self, market_data_service: MarketDataService, strategy_service: StrategyService
    ):
        self.market_data_service = market_data_service
        self.strategy_service = strategy_service

    async def execute_integrated_backtest(
        self,
        backtest_id: str,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        strategy_type: StrategyType,
        strategy_params: dict[str, Any],
        initial_capital: float = 100000.0,
    ) -> BacktestResult | None:
        """통합 백테스트 실행"""

        backtest = None
        execution = None

        try:
            # 1. 백테스트 조회 및 상태 업데이트
            backtest = await Backtest.get(PydanticObjectId(backtest_id))
            if not backtest:
                logger.error(f"Backtest not found: {backtest_id}")
                return None

            backtest.status = BacktestStatus.RUNNING
            backtest.start_time = datetime.now(UTC)
            await backtest.save()

            # 2. 실행 기록 생성
            execution = BacktestExecution(
                backtest_id=str(backtest.id),
                execution_id=f"exec_{datetime.now(UTC).timestamp()}_{backtest_id}",
                status=BacktestStatus.RUNNING,
                start_time=datetime.now(UTC),
                end_time=None,
                error_message=None,
            )
            await execution.insert()

            logger.info(f"Starting integrated backtest execution: {backtest_id}")

            # 3. 시장 데이터 수집
            market_data_dict = {}
            for symbol in symbols:
                try:
                    data = await self.market_data_service.get_market_data(
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                        force_refresh=False,
                    )
                    if data:
                        market_data_dict[symbol] = data
                        logger.info(f"Collected data for {symbol}: {len(data)} records")
                except Exception as e:
                    logger.error(f"Failed to collect data for {symbol}: {e}")

            if not market_data_dict:
                raise Exception("No market data collected")

            # 4. 전략 인스턴스 생성
            strategy_instance = await self.strategy_service.get_strategy_instance(
                strategy_type=strategy_type, parameters=strategy_params
            )

            if not strategy_instance:
                raise Exception(f"Failed to create strategy instance: {strategy_type}")

            # 5. 백테스트 시뮬레이션 실행
            trades, portfolio_values = await self._execute_simulation(
                strategy_instance=strategy_instance,
                market_data=market_data_dict,
                initial_capital=initial_capital,
                symbols=symbols,
            )

            # 6. 성과 분석
            performance = self._calculate_performance_metrics(
                portfolio_values=portfolio_values,
                initial_capital=initial_capital,
                trades=trades,
            )

            # 7. 결과 저장
            result = BacktestResult(
                backtest_id=str(backtest.id),
                execution_id=str(execution.id),
                performance=performance,
                final_portfolio_value=(
                    portfolio_values[-1] if portfolio_values else initial_capital
                ),
                cash_remaining=0.0,  # 체크 필요
                total_invested=initial_capital,
                var_95=None,
                var_99=None,
                calmar_ratio=None,
                sortino_ratio=None,
                benchmark_return=None,
                alpha=None,
                beta=None,
            )
            await result.insert()

            # 8. 백테스트 완료 처리
            backtest.status = BacktestStatus.COMPLETED
            backtest.end_time = datetime.now(UTC)
            backtest.duration_seconds = (
                backtest.end_time - backtest.start_time
            ).total_seconds()
            backtest.performance = performance
            await backtest.save()

            execution.status = BacktestStatus.COMPLETED
            execution.end_time = datetime.now(UTC)
            execution.trades = trades
            execution.portfolio_values = portfolio_values
            await execution.save()

            logger.info(f"Integrated backtest completed successfully: {backtest_id}")
            return result

        except Exception as e:
            logger.error(f"Integrated backtest execution failed: {e}")

            # 실패 처리
            if backtest:
                backtest.status = BacktestStatus.FAILED
                backtest.end_time = datetime.now(UTC)
                backtest.error_message = str(e)
                await backtest.save()

            if execution:
                execution.status = BacktestStatus.FAILED
                execution.end_time = datetime.now(UTC)
                execution.error_message = str(e)
                await execution.save()

            return None

    async def _execute_simulation(
        self,
        strategy_instance,
        market_data: dict[str, list],
        initial_capital: float,
        symbols: list[str],
    ) -> tuple[list[Trade], list[float]]:
        """백테스트 시뮬레이션 실행"""

        trades = []
        portfolio_values = [initial_capital]
        current_capital = initial_capital
        positions = {}  # symbol -> quantity

        # 가장 짧은 데이터 길이에 맞춤
        min_length = min(len(data) for data in market_data.values() if data)

        if min_length == 0:
            return trades, portfolio_values

        # 각 날짜별로 시뮬레이션
        for i in range(min_length):
            day_data = {}
            for symbol in symbols:
                if symbol in market_data and i < len(market_data[symbol]):
                    day_data[symbol] = market_data[symbol][i]

            if not day_data:
                continue

            # 전략 신호 생성
            try:
                signals = await strategy_instance.generate_signals(day_data)

                # 신호 기반 거래 실행
                day_trades = self._execute_trades(
                    signals=signals,
                    day_data=day_data,
                    positions=positions,
                    current_capital=current_capital,
                )

                trades.extend(day_trades)

                # 거래 후 자본 업데이트
                for trade in day_trades:
                    if trade.trade_type == TradeType.BUY:
                        current_capital -= (
                            trade.price * trade.quantity + trade.commission
                        )
                    else:
                        current_capital += (
                            trade.price * trade.quantity - trade.commission
                        )

                # 포트폴리오 가치 계산
                portfolio_value = self._calculate_portfolio_value(
                    positions=positions, day_data=day_data, cash=current_capital
                )

                portfolio_values.append(portfolio_value)

            except Exception as e:
                logger.warning(f"Strategy execution failed on day {i}: {e}")
                portfolio_values.append(portfolio_values[-1])  # 이전 값 유지

        return trades, portfolio_values

    def _execute_trades(
        self,
        signals: dict[str, Any],
        day_data: dict[str, Any],
        positions: dict[str, int],
        current_capital: float,
    ) -> list[Trade]:
        """거래 신호 기반 실제 거래 실행"""

        trades = []

        for symbol, signal in signals.items():
            if symbol not in day_data:
                continue

            price = day_data[symbol].get("close", 0)
            if price <= 0:
                continue

            signal_type = signal.get("action")
            quantity = signal.get("quantity", 0)

            if signal_type == "BUY" and quantity > 0:
                cost = price * quantity
                commission = cost * 0.001  # 0.1% 수수료
                total_cost = cost + commission

                if total_cost <= current_capital:
                    # 매수 실행
                    trade = Trade(
                        trade_id=f"trade_{datetime.now(UTC).timestamp()}_{symbol}_BUY",
                        symbol=symbol,
                        trade_type=TradeType.BUY,
                        quantity=quantity,
                        price=price,
                        timestamp=day_data[symbol].get("date", datetime.now(UTC)),
                        commission=commission,
                        strategy_signal_id=None,
                        notes=None,
                    )
                    trades.append(trade)
                    positions[symbol] = positions.get(symbol, 0) + quantity

            elif signal_type == "SELL" and quantity > 0:
                current_position = positions.get(symbol, 0)
                sell_quantity = min(quantity, current_position)

                if sell_quantity > 0:
                    # 매도 실행
                    revenue = price * sell_quantity
                    commission = revenue * 0.001  # 0.1% 수수료

                    trade = Trade(
                        trade_id=f"trade_{datetime.now(UTC).timestamp()}_{symbol}_SELL",
                        symbol=symbol,
                        trade_type=TradeType.SELL,
                        quantity=sell_quantity,
                        price=price,
                        timestamp=day_data[symbol].get("date", datetime.now(UTC)),
                        commission=commission,
                        strategy_signal_id=None,
                        notes=None,
                    )
                    trades.append(trade)
                    positions[symbol] -= sell_quantity

        return trades

    def _calculate_portfolio_value(
        self, positions: dict[str, int], day_data: dict[str, Any], cash: float
    ) -> float:
        """포트폴리오 총 가치 계산"""

        total_value = cash

        for symbol, quantity in positions.items():
            if symbol in day_data and quantity > 0:
                price = day_data[symbol].get("close", 0)
                total_value += price * quantity

        return total_value

    def _calculate_performance_metrics(
        self, portfolio_values: list[float], initial_capital: float, trades: list[Trade]
    ) -> PerformanceMetrics:
        """성과 지표 계산"""

        if len(portfolio_values) < 2:
            return PerformanceMetrics(
                total_return=0.0,
                annualized_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
            )

        final_value = portfolio_values[-1]
        total_return = (final_value - initial_capital) / initial_capital

        # 일일 수익률 계산
        daily_returns = []
        for i in range(1, len(portfolio_values)):
            if portfolio_values[i - 1] > 0:
                daily_return = (
                    portfolio_values[i] - portfolio_values[i - 1]
                ) / portfolio_values[i - 1]
                daily_returns.append(daily_return)

        # 연환산 수익률
        days = len(portfolio_values)
        annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0.0

        # 변동성
        volatility = np.std(daily_returns) * np.sqrt(252) if daily_returns else 0.0

        # 샤프 비율
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0.0

        # 최대 낙폭
        max_drawdown = self._calculate_max_drawdown(portfolio_values)

        # 거래 성과
        win_rate, winning_trades, losing_trades = self._calculate_trade_metrics(trades)
        total_trades = len(trades)

        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
        )

    def _calculate_max_drawdown(self, values: list[float]) -> float:
        """최대 낙폭 계산"""
        if not values:
            return 0.0

        peak = values[0]
        max_dd = 0.0

        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, drawdown)

        return max_dd

    def _calculate_trade_metrics(self, trades: list[Trade]) -> tuple[float, int, int]:
        """거래 성과 지표 계산"""
        if not trades or len(trades) < 2:
            return 0.0, 0, 0

        # 매수/매도 쌍 찾기
        winning_trades = 0
        total_trades = 0
        gross_profit = 0.0
        gross_loss = 0.0

        # 간단한 FIFO 방식으로 거래 쌍 계산
        positions = {}

        for trade in trades:
            symbol = trade.symbol

            if trade.trade_type == TradeType.BUY:
                if symbol not in positions:
                    positions[symbol] = []
                positions[symbol].append(trade)

            elif trade.trade_type == TradeType.SELL and symbol in positions:
                remaining_quantity = trade.quantity

                while remaining_quantity > 0 and positions[symbol]:
                    buy_trade = positions[symbol][0]

                    if buy_trade.quantity <= remaining_quantity:
                        # 전체 포지션 청산
                        profit = (trade.price - buy_trade.price) * buy_trade.quantity
                        total_trades += 1

                        if profit > 0:
                            winning_trades += 1
                            gross_profit += profit
                        else:
                            gross_loss += abs(profit)

                        remaining_quantity -= buy_trade.quantity
                        positions[symbol].pop(0)

                    else:
                        # 부분 청산
                        profit = (trade.price - buy_trade.price) * remaining_quantity
                        total_trades += 1

                        if profit > 0:
                            winning_trades += 1
                            gross_profit += profit
                        else:
                            gross_loss += abs(profit)

                        buy_trade.quantity -= remaining_quantity
                        remaining_quantity = 0

        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        losing_trades = total_trades - winning_trades

        return win_rate, winning_trades, losing_trades
