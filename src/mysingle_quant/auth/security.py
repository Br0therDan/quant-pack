from datetime import UTC, datetime, timedelta
from typing import Any, Union

import jwt
from jwt.exceptions import InvalidTokenError, PyJWTError
from pydantic import SecretStr

from ..core.config import settings
from ..core.logging_config import get_logger
from .schemas.auth import AccessTokenData, RefreshTokenData

logger = get_logger(__name__)
SecretType = Union[str, SecretStr]
ALGORITHM = settings.ALGORITHM


class JWTStrategyDestroyNotSupportedError(Exception):
    def __init__(self) -> None:
        message = "A JWT can't be invalidated: it's valid until it expires."
        super().__init__(message)


def _get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
    data: dict,
    lifetime_seconds: int | None = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
) -> str:
    payload = data.copy()
    now = datetime.now(UTC)
    payload["iat"] = int(now.timestamp())

    if lifetime_seconds:
        expire = now + timedelta(seconds=lifetime_seconds)
        payload["exp"] = int(expire.timestamp())

    return jwt.encode(
        payload, _get_secret_value(settings.SECRET_KEY), algorithm=ALGORITHM
    )


def decode_jwt(
    token: str,
    audience: list[str],
) -> dict[str, Any]:
    return jwt.decode(
        token,
        _get_secret_value(settings.SECRET_KEY),
        audience=audience,
        algorithms=[ALGORITHM],
    )


def create_auth_tokens(
    access_token_data: AccessTokenData,
    refresh_token_data: RefreshTokenData,
) -> tuple[str, str]:
    """
    JWT Access/Refresh 토큰 생성
    """
    try:
        access_token = jwt.encode(
            access_token_data.model_dump(),
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
    except PyJWTError as e:
        logger.error(f"Failed to generate access token: {e}")
        raise

    # Refresh Token 생성
    try:
        refresh_token = jwt.encode(
            refresh_token_data.model_dump(),
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
    except PyJWTError as e:
        logger.error(f"Failed to generate refresh token: {e}")
        raise

    return access_token, refresh_token


def validate_token(token: str) -> dict:
    """
    JWT 토큰 검증하고 payload를 dict로 반환
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except InvalidTokenError as e:
        logger.error(f"Token validation failed: {e}")
        raise ValueError("Invalid token")
