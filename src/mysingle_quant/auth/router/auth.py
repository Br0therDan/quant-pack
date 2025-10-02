"""Health check utilities and endpoints."""

from fastapi import APIRouter, Depends, Request, status

from ...core.config import settings
from ...core.logging_config import get_logger
from ..deps import get_current_active_verified_user
from ..exceptions import AuthenticationFailed, UserInactive, UserNotExists
from ..jwt import generate_jwt
from ..models import User
from ..schemas.auth import LoginRequest, LoginResponse
from ..schemas.user import UserResponse
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
        login_data: LoginRequest,
    ) -> LoginResponse:
        user = await user_manager.authenticate(
            username=login_data.username, password=login_data.password
        )

        if user is None:
            raise UserNotExists(identifier=login_data.username)

        if not user.is_active:
            raise UserInactive(user_id=str(user.id))

        if not user.is_verified:
            raise AuthenticationFailed("User not verified")

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": ["fastapi-users"],
        }
        token = generate_jwt(
            token_data, lifetime_seconds=access_token_expire_minutes * 60
        )
        logger.info(f"User {user.email} logged in.")
        # User 객체를 dict로 변환하면서 ObjectId를 문자열로 변환
        user_dict = user.model_dump()
        user_dict["id"] = str(user.id)  # ObjectId를 문자열로 변환
        user_info = UserResponse.model_validate(user_dict)
        response = LoginResponse(
            access_token=token, token_type="bearer", user_info=user_info.model_dump()
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

    return router
