from fastapi import APIRouter, Body, HTTPException, Request, status
from pydantic import EmailStr

from ..exceptions import (
    InvalidPasswordException,
    InvalidResetPasswordToken,
    UserInactive,
    UserNotExists,
)
from ..user_manager import UserManager
from .common import ErrorCode

user_manager = UserManager()


def get_reset_password_router() -> APIRouter:
    """Generate a router with the reset password routes."""
    router = APIRouter()

    @router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
        name="reset:forgot_password",
    )
    async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
    ):
        try:
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            return None

        try:
            await user_manager.forgot_password(user, request)
        except UserInactive:
            pass

        return None

    @router.post(
        "/reset-password",
        name="reset:reset_password",
    )
    async def reset_password(
        request: Request,
        token: str = Body(...),
        password: str = Body(...),
    ):
        try:
            await user_manager.reset_password(token, password, request)
        except (
            InvalidResetPasswordToken,
            UserNotExists,
            UserInactive,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    return router
