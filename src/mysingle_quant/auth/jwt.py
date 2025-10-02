from datetime import UTC, datetime, timedelta
from typing import Any, Union

import jwt
from pydantic import SecretStr

from ..auth.models import User
from ..core.config import settings

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
    if lifetime_seconds:
        expire = datetime.now(UTC) + timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
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


async def write_token(user: User) -> str:
    data = {"sub": str(user.id), "aud": ["fastapi-users"]}
    return generate_jwt(data, lifetime_seconds=3600)


async def destroy_token(token: str, user: User) -> None:
    raise JWTStrategyDestroyNotSupportedError()
