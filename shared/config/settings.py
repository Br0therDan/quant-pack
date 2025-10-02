"""
애플리케이션 설정 클래스

환경 변수와 설정 파일을 통해 애플리케이션 설정을 관리합니다.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    # Alpha Vantage API 설정
    alphavantage_api_key: str = Field(
        default="", description="Alpha Vantage API 키", alias="ALPHAVANTAGE_API_KEY"
    )
    alphavantage_base_url: str = Field(
        default="https://www.alphavantage.co/query",
        description="Alpha Vantage API Base URL",
        alias="ALPHAVANTAGE_BASE_URL",
    )

    # 데이터베이스 설정
    database_path: str = Field(
        default="./data/quant.db",
        description="데이터베이스 파일 경로",
        alias="DATABASE_PATH",
    )

    # 캐시 설정
    cache_ttl_hours: int = Field(
        default=24, description="캐시 TTL (시간)", alias="CACHE_TTL_HOURS"
    )

    # API 레이트 리미팅
    api_calls_per_minute: int = Field(
        default=5, description="분당 API 호출 제한", alias="API_CALLS_PER_MINUTE"
    )
    api_calls_per_day: int = Field(
        default=500, description="일일 API 호출 제한", alias="API_CALLS_PER_DAY"
    )

    # 로깅 설정
    log_level: str = Field(default="INFO", description="로그 레벨", alias="LOG_LEVEL")
    log_file_path: str | None = Field(
        default=None, description="로그 파일 경로", alias="LOG_FILE_PATH"
    )

    # 백테스트 설정
    default_commission: float = Field(
        default=0.001, description="기본 수수료 (0.1%)", alias="DEFAULT_COMMISSION"
    )
    default_slippage: float = Field(
        default=0.0005, description="기본 슬리피지 (0.05%)", alias="DEFAULT_SLIPPAGE"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


# 전역 설정 인스턴스 생성 함수
def get_settings() -> Settings:
    """설정 인스턴스를 반환합니다."""
    return Settings()


# 편의를 위한 전역 인스턴스
settings = get_settings()
