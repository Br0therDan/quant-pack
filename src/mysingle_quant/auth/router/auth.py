"""Health check utilities and endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Cookie, Depends, Header, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from ...core.config import settings
from ...core.logging_config import get_logger
from ..deps import get_current_active_verified_user
from ..exceptions import AuthenticationFailed, UserInactive, UserNotExists
from ..models import User
from ..schemas.auth import AccessTokenData, LoginResponse, RefreshTokenData
from ..schemas.user import UserResponse
from ..security import create_auth_tokens, validate_token
from ..user_manager import UserManager

logger = get_logger(__name__)
access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
user_manager = UserManager()


def create_auth_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/login",
        response_model=LoginResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def login(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> LoginResponse:
        user = await user_manager.authenticate(
            username=form_data.username, password=form_data.password
        )

        if user is None:
            raise UserNotExists(identifier=form_data.username)

        if not user.is_active:
            raise UserInactive(user_id=str(user.id))

        if not user.is_verified:
            raise AuthenticationFailed("User not verified")

        now = datetime.now(UTC)
        access_exp = int(
            (now + timedelta(minutes=access_token_expire_minutes)).timestamp()
        )
        refresh_exp = int(
            (now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
        )

        logger.info(f"Creating tokens for user {user.email}")
        logger.info(f"Current time: {now.isoformat()}")
        logger.info(
            f"Access token expires at: {datetime.fromtimestamp(access_exp, UTC).isoformat()}"
        )
        logger.info(
            f"Refresh token expires at: {datetime.fromtimestamp(refresh_exp, UTC).isoformat()}"
        )

        access_token_data = AccessTokenData(
            sub=str(user.id),
            email=user.email,
            exp=access_exp,
            iat=int(now.timestamp()),
            aud=["quant-users"],  # TODO: audience 설정 옵션 추가 필요
        )
        refresh_token_data = RefreshTokenData(
            sub=str(user.id),
            exp=refresh_exp,
            iat=int(now.timestamp()),
            aud=["quant-users"],  # TODO: audience 설정 옵션 추가 필요
        )

        access_token, refresh_token = create_auth_tokens(
            access_token_data=access_token_data,
            refresh_token_data=refresh_token_data,
        )

        response = LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_info=UserResponse(**user.model_dump(by_alias=True)),
        )

        await user_manager.on_after_login(user, request)
        return response

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(
        request: Request,
        current_user: User = Depends(get_current_active_verified_user),
    ) -> None:
        """
        로그아웃 엔드포인트.

        현재는 클라이언트 측에서 토큰을 삭제하는 방식으로 처리합니다.
        JWT 토큰은 서버에서 무효화할 수 없으므로, 클라이언트에서 토큰을 삭제해야 합니다.
        """
        # 로그아웃 후 처리 로직 실행
        await user_manager.on_after_logout(current_user, request)
        # HTTP 204는 응답 본문이 없어야 하므로 None 반환
        return None

    @router.post("/refresh", response_model=LoginResponse)
    async def refresh_token(
        request: Request,
        refresh_token_header: str | None = Header(None, alias="X-Refresh-Token"),
        refresh_token_cookie: str | None = Cookie(None, alias="refresh_token"),
    ) -> LoginResponse:
        """
        JWT 토큰 갱신 엔드포인트.

        현재는 Access Token과 Refresh Token을 모두 새로 발급합니다.
        """
        refresh_token = refresh_token_header or refresh_token_cookie
        if not refresh_token:
            raise AuthenticationFailed("Refresh token not provided")
        payload = validate_token(refresh_token)

        if payload.aud != ["quant-users"]:
            raise AuthenticationFailed("Invalid token audience")
        user_id = payload.sub
        user = await user_manager.get(PydanticObjectId(user_id))

        access_token_data = AccessTokenData(
            sub=str(user.id),
            email=user.email,
            exp=access_token_expire_minutes * 60,
            iat=0,
            aud=["quant-users"],  # TODO: audience 설정 옵션 추가 필요
        )
        refresh_token_data = RefreshTokenData(
            sub=str(user.id),
            exp=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            iat=0,
            aud=["quant-users"],  # TODO: audience 설정 옵션 추가 필요
        )

        access_token, refresh_token = create_auth_tokens(
            access_token_data=access_token_data,
            refresh_token_data=refresh_token_data,
        )

        response = LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_info=UserResponse(**user.model_dump(by_alias=True)),
        )

        await user_manager.on_after_login(user, request)
        return response

    @router.get("/token/verify")
    async def verify_token(
        current_user: User = Depends(get_current_active_verified_user),
    ) -> dict:
        """토큰 검증 및 사용자 정보 반환 (디버깅용)"""
        return {
            "valid": True,
            "user_id": str(current_user.id),
            "email": current_user.email,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "is_superuser": current_user.is_superuser,
        }

    return router
