# path: app/schemas/oauth2.py
from typing import Optional

from pydantic import BaseModel


# -------------------
# 공통 토큰 스키마 (필요한 필드만 선언)
# -------------------
class BaseOAuthToken(BaseModel):
    access_token: str
    token_type: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    expires_at: Optional[int] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None
    refresh_token_expires_in: Optional[int] = None


# -------------------
# 구글
# -------------------
class GoogleToken(BaseOAuthToken):
    # 기존에 없는 필드 id_token 등 이미 BaseOAuthToken에 들어있으면 중복 필요 X
    pass


class GoogleProfile(BaseModel):
    id: str
    email: str
    verified_email: bool
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    hd: Optional[str] = None


# -------------------
# 카카오
# -------------------
class KakaoToken(BaseOAuthToken):
    # e.g. Kakao 전용 필드가 있으면 여기에
    pass


class KakaoProfile(BaseModel):
    id: int
    connected_at: str

    # 실제로는 kakao_account 구조
    # 여기서는 간단히 예시
    class KakaoAccount(BaseModel):
        email: str

        class Profile(BaseModel):
            nickname: str
            profile_image_url: Optional[str]

        profile: Profile

    kakao_account: KakaoAccount


# -------------------
# 네이버
# -------------------
class NaverToken(BaseOAuthToken):
    pass


class NaverProfile(BaseModel):
    id: str
    nickname: str
    profile_image: str
    email: str
    name: str
