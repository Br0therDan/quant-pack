from fastapi import Response

from ..core.config import settings


def set_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=settings.HTTPONLY_COOKIES,
        samesite=settings.SAMESITE_COOKIES,
        secure=settings.ENVIRONMENT == "production",
    )


def delete_cookie(response: Response, key: str) -> None:
    response.delete_cookie(key)
