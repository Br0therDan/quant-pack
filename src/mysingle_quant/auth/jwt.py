from typing import Any, Union

import jwt
from pydantic import SecretStr


def generate_jwt(payload: dict, key: Union[str, SecretStr], algorithm: str) -> str:
    payload = payload.copy()

    return jwt.encode(
        payload,
        key=key.get_secret_value() if isinstance(key, SecretStr) else key,
        algorithm=algorithm,
    )


def decode_jwt(
    token: str,
    key: Union[str, SecretStr],
    audience: list[str],
    algorithms: list[str] = ["HS256"],
) -> dict[str, Any]:
    return jwt.decode(
        token,
        key=key.get_secret_value() if isinstance(key, SecretStr) else key,
        audience=audience,
        algorithms=algorithms,
    )
