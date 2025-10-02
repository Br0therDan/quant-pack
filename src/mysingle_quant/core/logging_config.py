"""
로깅 설정 모듈
"""

import logging
import sys
from pathlib import Path


def setup_logging():
    """애플리케이션 로깅 설정"""

    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 로그 포맷 설정
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 (일반 로그)
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # 에러 로그 파일 핸들러
    error_handler = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(log_format)
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

    # 이메일 관련 로거 설정
    email_logger = logging.getLogger("app.utils.email")
    email_logger.setLevel(logging.INFO)

    # 유저 관리 로거 설정
    user_logger = logging.getLogger("app.services.user_manager")
    user_logger.setLevel(logging.INFO)

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info("Logging configuration setup completed")


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스를 가져오는 헬퍼 함수"""
    return logging.getLogger(name)
