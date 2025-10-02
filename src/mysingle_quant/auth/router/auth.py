"""Health check utilities and endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...core.config import settings
from ..deps import get_current_active_verified_user
from ..jwt import generate_jwt
from ..models import User
from ..schemas.auth import LoginRequest, LoginResponse
from ..schemas.user import UserResponse
from ..user_manager import UserManager

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
    ):
        user = await user_manager.authenticate(
            username=login_data.username, password=login_data.password
        )

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials or inactive user.",
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not verified.",
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": ["fastapi-users"],
        }
        token = generate_jwt(
            token_data, lifetime_seconds=access_token_expire_minutes * 60
        )
        user_info = UserResponse.model_validate(user, from_attributes=True)
        response = LoginResponse(
            access_token=token, token_type="bearer", user_info=user_info.model_dump()
        )

        await user_manager.on_after_login(user, request)
        return response

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(
        current_user: User = Depends(get_current_active_verified_user),
    ):
        """로그아웃 엔드포인트. 현재는 클라이언트 측에서 "
        "토큰을 삭제하는 방식으로 처리합니다."""
        return {"message": "Successfully logged out"}

    return router
