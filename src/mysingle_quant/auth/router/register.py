from fastapi import APIRouter, HTTPException, Request, status

from ..exceptions import (
    InvalidPasswordException,
    UserAlreadyExists,
)
from ..schemas import UserCreate, UserResponse
from ..user_manager import UserManager
from .common import ErrorCode

user_manager = UserManager()


def get_register_router() -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register(
        request: Request,
        obj_in: UserCreate,
    ):
        try:
            created_user = await user_manager.create(obj_in, request=request)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

        return UserResponse.model_validate(created_user, from_attributes=True)

    return router
