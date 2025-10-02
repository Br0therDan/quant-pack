from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user_info: dict


class AccessToken(BaseModel):
    sub: str
    exp: int
    type: str = "access"
    email: str


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str
