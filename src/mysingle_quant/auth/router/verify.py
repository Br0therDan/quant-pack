from exceptions import (
    InvalidVerifyToken,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from fastapi import APIRouter, Body, HTTPException, Request, status
from pydantic import EmailStr

from ..schemas import UserResponse
from ..user_manager import UserManager
from .common import ErrorCode

user_manager = UserManager()


def get_verify_router():
    router = APIRouter()

    @router.post(
        "/request-verify-token",
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def request_verify_token(
        request: Request,
        email: EmailStr = Body(..., embed=True),
    ):
        try:
            user = await user_manager.get_by_email(email)
            await user_manager.request_verify(user, request)
        except (
            UserNotExists,
            UserInactive,
            UserAlreadyVerified,
        ):
            pass

        return None

    @router.post(
        "/verify",
        response_model=UserResponse,
    )
    async def verify(
        request: Request,
        token: str = Body(..., embed=True),
    ):
        try:
            user = await user_manager.verify(token, request)
            return UserResponse.model_validate(user, from_attributes=True)
        except (InvalidVerifyToken, UserNotExists):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )
        except UserAlreadyVerified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
            )

    return router
