from pydantic import ConfigDict, EmailStr, Field

from mysingle_quant.core.base import BaseDoc


class User(BaseDoc):
    """Base User Document model."""

    email: EmailStr
    hashed_password: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    oauth_accounts: list["OAuthAccount"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class OAuthAccount(BaseDoc):
    """Base OAuth account Document model."""

    oauth_name: str
    access_token: str
    account_id: str
    account_email: str
    expires_at: int | None = None
    refresh_token: str | None = None

    model_config = ConfigDict(from_attributes=True)
