"""
CLI 모듈

서비스별로 분리된 CLI 명령어들을 관리합니다.
"""

from shared.cli.backtest_commands import backtest_app
from shared.cli.data_commands import data_app
from shared.cli.main import app
from shared.cli.report_commands import report_app
from shared.cli.strategy_commands import strategy_app

__all__ = ["app", "data_app", "strategy_app", "backtest_app", "report_app"]
