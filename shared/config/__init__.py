"""
애플리케이션 설정 관리

이 모듈은 환경 변수, 설정 파일 등을 통해 애플리케이션 설정을 관리합니다.
Pydantic Settings를 사용하여 타입 안전한 설정 관리를 제공합니다.
"""

from __future__ import annotations

from .settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
