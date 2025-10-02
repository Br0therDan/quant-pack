from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    """Base User model."""

    id: str = Field(..., alias="_id")
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    oauth_accounts: list["OAuthAccount"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False


class UserUpdate(BaseModel):
    password: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class OAuthAccount(BaseModel):
    """Base OAuth account model."""

    id: str = Field(..., alias="_id")
    oauth_name: str
    access_token: str
    expires_at: int | None = None
    refresh_token: str | None = None
    account_id: str
    account_email: str

    model_config = ConfigDict(from_attributes=True)
