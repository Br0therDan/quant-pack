from datetime import UTC, datetime, timedelta
from typing import Any, Union

import jwt
from pydantic import SecretStr

from ..auth.exceptions import InvalidID, UserNotExists
from ..auth.models import User
from ..auth.user_manager import UserManager
from ..core.config import settings

SecretType = Union[str, SecretStr]
ALGORITHM = settings.ALGORITHM
user_manager = UserManager()


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


async def read_token(
    encoded_token: str | None,
    token_audience: list[str] = ["fastapi-users"],
) -> User | None:
    if encoded_token is None:
        return None
    try:
        data = decode_jwt(encoded_token, token_audience)
        user_id = data.get("sub")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None

    try:
        parsed_id = user_manager.parse_id(user_id)
        user = await user_manager.get(parsed_id)
        return user
    except (UserNotExists, InvalidID):
        return None


async def write_token(user: User) -> str:
    data = {"sub": str(user.id), "aud": ["fastapi-users"]}
    return generate_jwt(data, lifetime_seconds=3600)


async def destroy_token(token: str, user: User) -> None:
    raise JWTStrategyDestroyNotSupportedError()
