"""
전략 서비스 CLI 명령어

전략 관리, 생성, 검증, 테스트 관련 명령어들을 제공합니다.
"""

import typer
from rich.console import Console
from rich.table import Table

strategy_app = typer.Typer(help="전략 관리 명령어")
console = Console()


@strategy_app.command("list")
def list_strategies(
    strategy_type: str = typer.Option(None, "--type", help="전략 타입 필터"),
) -> None:
    """전략 템플릿 목록 조회"""
    try:
        from services.strategy_service.strategy_manager import get_strategy_manager

        manager = get_strategy_manager()
        templates = manager.list_templates(strategy_type)

        if not templates:
            console.print("[yellow]등록된 전략 템플릿이 없습니다.[/yellow]")
            return

        table = Table(title=f"전략 템플릿 목록 ({len(templates)}개)")
        table.add_column("이름", style="cyan")
        table.add_column("타입", style="green")
        table.add_column("설명", style="yellow")
        table.add_column("태그", style="blue")

        for template in templates:
            tags_str = ", ".join(template.tags) if template.tags else "-"
            # strategy_type이 enum이면 .value를, 문자열이면 그대로 사용
            strategy_type_str = (
                template.strategy_type.value
                if hasattr(template.strategy_type, "value")
                else str(template.strategy_type)
            )
            table.add_row(
                template.name,
                strategy_type_str,
                (
                    template.description[:50] + "..."
                    if len(template.description) > 50
                    else template.description
                ),
                tags_str,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]오류: {e}[/red]")


@strategy_app.command("create")
def create_strategy(
    strategy_type: str = typer.Argument(
        ...,
        help="전략 타입 (sma_crossover, rsi_mean_reversion, momentum, buy_and_hold)",
    ),
    name: str = typer.Option(None, "--name", help="전략 이름"),
    template: str = typer.Option(None, "--template", help="템플릿 이름"),
) -> None:
    """새 전략 생성"""
    try:
        from services.strategy_service.strategy_manager import (
            StrategyType,
            get_strategy_manager,
        )

        manager = get_strategy_manager()

        # 템플릿 기반 생성
        if template:
            strategy = manager.create_strategy_from_template(template, name)
            console.print(
                f"[green]템플릿 '{template}'로부터 전략 '{strategy.name}' 생성 완료[/green]"
            )
        else:
            # 기본 파라미터로 생성
            try:
                strategy_type_enum = StrategyType(strategy_type)
            except ValueError:
                available_types = manager.get_available_strategy_types()
                console.print(f"[red]지원되지 않는 전략 타입: {strategy_type}[/red]")
                console.print(
                    f"[yellow]사용 가능한 타입: {', '.join(available_types)}[/yellow]"
                )
                return

            strategy = manager.create_strategy(strategy_type_enum, name)
            console.print(f"[green]전략 '{strategy.name}' 생성 완료[/green]")

        # 전략 정보 출력
        console.print(f"  타입: {strategy.__class__.__name__}")
        console.print(f"  설명: {strategy.description}")
        console.print(f"  파라미터: {len(strategy.parameters)}개")

    except Exception as e:
        console.print(f"[red]오류: {e}[/red]")


@strategy_app.command("validate")
def validate_strategy_config(
    strategy_type: str = typer.Argument(..., help="전략 타입"),
    config_file: str = typer.Option(None, "--config", help="설정 파일 경로 (JSON)"),
) -> None:
    """전략 설정 검증"""
    try:
        import json

        from services.strategy_service.strategy_manager import (
            StrategyType,
            get_strategy_manager,
        )

        manager = get_strategy_manager()

        try:
            strategy_type_enum = StrategyType(strategy_type)
        except ValueError:
            available_types = manager.get_available_strategy_types()
            console.print(f"[red]지원되지 않는 전략 타입: {strategy_type}[/red]")
            console.print(
                f"[yellow]사용 가능한 타입: {', '.join(available_types)}[/yellow]"
            )
            return

        if config_file:
            # 파일에서 설정 로드
            with open(config_file, encoding="utf-8") as f:
                parameters = json.load(f)
        else:
            # 기본 설정으로 검증
            parameters = {}

        # 설정 검증
        is_valid = manager.validate_strategy_config(strategy_type_enum, parameters)

        if is_valid:
            console.print("[green]✓ 전략 설정이 유효합니다[/green]")

            # 입력된 설정 출력
            table = Table(title="입력된 설정")
            table.add_column("파라미터", style="cyan")
            table.add_column("값", style="green")

            for key, value in parameters.items():
                table.add_row(key, str(value))

            console.print(table)
        else:
            console.print("[red]✗ 전략 설정이 유효하지 않습니다[/red]")

    except Exception as e:
        console.print(f"[red]설정 검증 실패: {e}[/red]")


@strategy_app.command("test")
def test_strategy(
    template_name: str = typer.Argument(..., help="테스트할 템플릿 이름"),
    symbol: str = typer.Option("AAPL", "--symbol", help="테스트용 심볼"),
    days: int = typer.Option(100, "--days", help="테스트 기간 (일)"),
) -> None:
    """전략 테스트 실행"""
    try:
        from datetime import datetime, timedelta

        import numpy as np
        import pandas as pd

        from services.strategy_service.strategy_manager import get_strategy_manager

        console.print(f"[cyan]전략 '{template_name}' 테스트 시작...[/cyan]")

        manager = get_strategy_manager()

        # 전략 생성
        strategy = manager.create_strategy_from_template(template_name)

        # 데이터 로드 시도
        try:
            from services.data_service import get_database

            db = get_database()

            # 최근 N일 데이터 가져오기 위한 날짜 계산
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            with db:
                data = db.get_daily_prices(
                    symbol, start_date=start_date, end_date=end_date
                )

            if data.empty:
                console.print(
                    f"[yellow]심볼 {symbol}의 데이터가 없습니다. 모의 데이터를 생성합니다.[/yellow]"
                )
                raise ValueError("No data")

        except Exception:
            # 모의 데이터 생성
            console.print("[yellow]모의 데이터로 테스트를 진행합니다.[/yellow]")

            dates = pd.date_range("2023-01-01", periods=days, freq="D")
            np.random.seed(42)

            prices = []
            price = 100
            for _ in range(days):
                price *= 1 + np.random.randn() * 0.02
                prices.append(max(price, 50))  # 최소값 제한

            data = pd.DataFrame(
                {
                    "date": dates,
                    "open": prices,
                    "high": [p * 1.02 for p in prices],
                    "low": [p * 0.98 for p in prices],
                    "close": prices,
                    "volume": np.random.randint(1000, 10000, days),
                    "symbol": symbol,
                }
            ).set_index("date")

        # 전략 실행
        signals = strategy.run(data)

        # 성과 분석
        performance = manager.analyze_strategy_performance(strategy, data)

        # 결과 출력
        console.print("[green]테스트 완료![/green]")

        table = Table(title=f"전략 성과 - {strategy.name}")
        table.add_column("지표", style="cyan")
        table.add_column("값", style="green")

        table.add_row("총 신호", str(performance.total_signals))
        table.add_row("매수 신호", str(performance.buy_signals))
        table.add_row("매도 신호", str(performance.sell_signals))

        if performance.total_return:
            table.add_row("총 수익률", f"{performance.total_return:.2%}")
        if performance.win_rate:
            table.add_row("승률", f"{performance.win_rate:.2%}")
        if performance.avg_return_per_trade:
            table.add_row("평균 거래 수익률", f"{performance.avg_return_per_trade:.2%}")

        console.print(table)

        # 최근 신호 출력
        if signals:
            recent_signals = signals[-5:]
            signal_table = Table(title="최근 신호")
            signal_table.add_column("시간", style="cyan")
            signal_table.add_column("타입", style="green")
            signal_table.add_column("가격", style="yellow")
            signal_table.add_column("강도", style="blue")

            for signal in recent_signals:
                signal_table.add_row(
                    signal.timestamp.strftime("%Y-%m-%d"),
                    signal.signal_type.value,
                    f"{signal.price:.2f}",
                    f"{signal.strength:.2f}",
                )

            console.print(signal_table)

    except Exception as e:
        console.print(f"[red]테스트 실패: {e}[/red]")


@strategy_app.command("compare")
def compare_strategies(
    templates: str = typer.Argument(..., help="비교할 템플릿들 (쉼표로 구분)"),
    symbol: str = typer.Option("AAPL", "--symbol", help="테스트용 심볼"),
    days: int = typer.Option(100, "--days", help="테스트 기간 (일)"),
) -> None:
    """여러 전략 성과 비교"""
    try:
        import numpy as np
        import pandas as pd

        from services.strategy_service.strategy_manager import get_strategy_manager

        template_list = [t.strip() for t in templates.split(",")]
        console.print(f"[cyan]전략 비교 시작: {', '.join(template_list)}[/cyan]")

        manager = get_strategy_manager()

        # 모의 데이터 생성
        dates = pd.date_range("2023-01-01", periods=days, freq="D")
        np.random.seed(42)

        prices = []
        price = 100
        for _ in range(days):
            price *= 1 + np.random.randn() * 0.02
            prices.append(max(price, 50))

        data = pd.DataFrame(
            {
                "date": dates,
                "open": prices,
                "high": [p * 1.02 for p in prices],
                "low": [p * 0.98 for p in prices],
                "close": prices,
                "volume": np.random.randint(1000, 10000, days),
                "symbol": symbol,
            }
        ).set_index("date")

        # 전략들 생성 및 실행
        strategies = []
        for template_name in template_list:
            try:
                strategy = manager.create_strategy_from_template(template_name)
                strategies.append(strategy)
            except Exception as e:
                console.print(
                    f"[yellow]템플릿 '{template_name}' 로드 실패: {e}[/yellow]"
                )

        if not strategies:
            console.print("[red]비교할 전략이 없습니다.[/red]")
            return

        # 성과 비교
        comparison = manager.compare_strategies(strategies, data)

        # 결과 테이블 출력
        table = Table(title="전략 성과 비교")
        table.add_column("전략", style="cyan")
        table.add_column("총 신호", style="green", justify="right")
        table.add_column("매수", style="green", justify="right")
        table.add_column("매도", style="green", justify="right")
        table.add_column("총 수익률", style="yellow", justify="right")
        table.add_column("승률", style="blue", justify="right")

        for _, row in comparison.iterrows():
            total_return = (
                f"{row['total_return']:.2%}" if row["total_return"] else "N/A"
            )
            win_rate = f"{row['win_rate']:.2%}" if row["win_rate"] else "N/A"

            table.add_row(
                row["strategy_name"],
                str(row["total_signals"]),
                str(row["buy_signals"]),
                str(row["sell_signals"]),
                total_return,
                win_rate,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]비교 실패: {e}[/red]")
