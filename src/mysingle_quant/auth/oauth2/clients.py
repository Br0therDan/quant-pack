from fastapi import APIRouter
from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.router import router as oauth2_router
from social_core.backends.google import GoogleOAuth2
from social_core.backends.kakao import KakaoOAuth2
from social_core.backends.naver import NaverOAuth2

from ...core.config import settings

router = APIRouter()


google_client = OAuth2Client(
    backend=GoogleOAuth2,
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    scope=["openid", "profile", "email"],
    # claims=Claims(
    #     identity=lambda user: f"{user.provider}:{user.sub}",
    # ),
)
kakao_client = OAuth2Client(
    backend=KakaoOAuth2,
    client_id=settings.KAKAO_CLIENT_ID,
    client_secret=settings.KAKAO_CLIENT_SECRET,
    scope=["profile_nickname", "account_email"],
    # claims=Claims(
    #     identity=lambda user: f"{user.provider}:{user.id}",
    # ),
)

naver_client = OAuth2Client(
    backend=NaverOAuth2,
    client_id=settings.NAVER_CLIENT_ID,
    client_secret=settings.NAVER_CLIENT_SECRET,
    scope=["name", "email"],
    # claims=Claims(
    #     identity=lambda user: f"{user.provider}:{user.id}",
    # ),
)


router.include_router(oauth2_router)
