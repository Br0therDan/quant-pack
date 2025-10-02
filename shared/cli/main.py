"""
메인 CLI 애플리케이션

모든 서비스의 CLI 명령어들을 통합합니다.
"""

import typer
from rich.console import Console

from shared.cli.backtest_commands import backtest_app

# 서브커맨드 앱들을 import
from shared.cli.data_commands import data_app
from shared.cli.report_commands import report_app
from shared.cli.strategy_commands import strategy_app

app = typer.Typer(help="퀀트 백테스트 앱")
console = Console()

# 서브커맨드 그룹들 등록
app.add_typer(data_app, name="data")
app.add_typer(strategy_app, name="strategy")
app.add_typer(backtest_app, name="backtest")
app.add_typer(report_app, name="report")


@app.command("version")
def show_version() -> None:
    """버전 정보 표시"""
    console.print("[cyan]퀀트 백테스트 앱 v0.1.0[/cyan]")


@app.command("status")
def show_status() -> None:
    """앱 상태 확인"""
    console.print("[cyan]시스템 상태 확인 중...[/cyan]")

    # 데이터베이스 연결 확인
    try:
        from services.data_service import get_database

        with get_database() as db:
            symbols = db.get_available_symbols()
            console.print(
                f"[green]✓ 데이터베이스 연결됨 ({len(symbols)}개 종목)[/green]"
            )

    except Exception as e:
        console.print(f"[red]✗ 데이터베이스 연결 실패: {e}[/red]")

    # API 키 확인
    try:
        from shared.config.settings import Settings

        settings = Settings()
        if settings.alphavantage_api_key:
            console.print("[green]✓ Alpha Vantage API 키 설정됨[/green]")
        else:
            console.print("[yellow]⚠ Alpha Vantage API 키 미설정[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ 설정 확인 실패: {e}[/red]")


if __name__ == "__main__":
    app()
