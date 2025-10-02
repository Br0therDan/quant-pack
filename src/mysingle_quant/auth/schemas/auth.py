from pydantic import BaseModel

from .user import UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {"username": "user@example.com", "password": "string"}
        }


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user_info: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "string",
                "refresh_token": "string",
                "token_type": "bearer",
                "user_info": {
                    "id": "string",
                    "email": "user@example.com",
                    "full_name": "string",
                    "is_active": True,
                    "is_superuser": False,
                    "is_verified": False,
                },
            }
        }


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://example.com/oauth/authorize?response_type=code&client_id=your_client_id&redirect_uri=your_redirect_uri&scope=your_scope"
            }
        }
