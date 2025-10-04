"""Health check utilities and endpoints."""

from typing import Annotated

from beanie import PydanticObjectId
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from ...core.config import settings
from ...core.logging_config import get_logger
from ..authenticate import authenticator
from ..deps import get_current_active_verified_user
from ..exceptions import AuthenticationFailed, UserInactive
from ..models import User
from ..schemas.auth import LoginResponse
from ..schemas.user import UserResponse
from ..user_manager import UserManager

logger = get_logger(__name__)
access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
user_manager = UserManager()
authenticator = authenticator


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

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise UserInactive()

        # FastAPI Response 객체가 필요하므로 Response를 생성
        from fastapi import Response

        response_obj = Response()

        # authenticator.login을 호출하여 토큰 생성
        token_data = authenticator.login(
            user=user,
            response=response_obj,
        )
        if token_data:  # Header 또는 Hybrid 방식일 때
            logger.debug(f"Generated token data: {token_data}")
            # 토큰 정보를 응답에 포함
            login_response = LoginResponse(
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                token_type=token_data["token_type"],
                user_info=UserResponse(**user.model_dump(by_alias=True)),
            )
        else:  # Cookie 방식일 때
            logger.debug("Token set in cookies")
            # 쿠키에 토큰이 설정되었으므로 토큰 값을 직접 전달하지 않음
            login_response = LoginResponse(
                user_info=UserResponse(**user.model_dump(by_alias=True)),
            )

        await user_manager.on_after_login(user, request)
        return login_response

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(
        request: Request,
        response: Response,
        current_user: User = Depends(get_current_active_verified_user),
    ) -> None:
        """
        로그아웃 엔드포인트.

        쿠키에서 토큰을 삭제하고 로그아웃 처리를 합니다.
        """
        # authenticator를 사용하여 쿠키 삭제
        authenticator.logout(response)

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

        # authenticator를 사용하여 토큰 검증 및 새 토큰 생성
        from fastapi import Response

        response_obj = Response()

        try:
            token_data = authenticator.refresh_token(
                refresh_token=refresh_token,
                response=response_obj,
                transport_type="header",
            )
        except HTTPException:
            raise AuthenticationFailed("Invalid refresh token")

        if not token_data:
            raise AuthenticationFailed("Failed to generate tokens")

        # 토큰에서 사용자 정보를 가져와서 응답에 포함
        try:
            payload = authenticator.validate_token(token_data["access_token"])
            user_id = payload.get("sub")
            user = await user_manager.get(PydanticObjectId(user_id))
            if not user:
                raise AuthenticationFailed("User not found")
        except Exception:
            raise AuthenticationFailed("Failed to retrieve user information")

        response = LoginResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
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
