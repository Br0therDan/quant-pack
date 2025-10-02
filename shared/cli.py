"""
CLI 인터페이스

Typer를 사용한 명령행 인터페이스를 제공합니다.
서비스별로 분리된 CLI 모듈을 통합합니다.
"""

from shared.cli.main import app

if __name__ == "__main__":
    app()
