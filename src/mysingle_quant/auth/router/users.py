from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ..deps import get_current_active_superuser, get_current_active_verified_user
from ..exceptions import (
    InvalidPasswordException,
    UserAlreadyExists,
)
from ..models import User
from ..schemas import UserResponse, UserUpdate
from ..user_manager import UserManager
from .common import ErrorCode

user_manager = UserManager()


def get_users_router() -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    @router.get(
        "/me",
        response_model=UserResponse,
    )
    async def get_user_me(
        current_user: User = Depends(get_current_active_verified_user),
    ):
        return UserResponse.model_validate(current_user, from_attributes=True)

    @router.patch(
        "/me",
        response_model=UserResponse,
        dependencies=[Depends(get_current_active_verified_user)],
    )
    async def update_user_me(
        request: Request,
        obj_in: UserUpdate,
        current_user: User = Depends(get_current_active_verified_user),
    ):
        try:
            user = await user_manager.update(
                obj_in, current_user, safe=True, request=request
            )
            return UserResponse.model_validate(user, from_attributes=True)
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except UserAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

    @router.get(
        "/{id}",
        response_model=UserResponse,
        dependencies=[Depends(get_current_active_superuser)],
    )
    async def get_user(id: PydanticObjectId):
        user = await user_manager.get(id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return UserResponse.model_validate(user)

    @router.patch(
        "/{id}",
        response_model=UserResponse,
        dependencies=[Depends(get_current_active_superuser)],
    )
    async def update_user(
        id: PydanticObjectId,
        obj_in: UserUpdate,  # type: ignore
        request: Request,
    ):
        try:
            user = await user_manager.get(id)
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            updated_user = await user_manager.update(
                obj_in, user, safe=False, request=request
            )
            return UserResponse.model_validate(updated_user, from_attributes=True)
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except UserAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

    @router.delete(
        "/{id}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        dependencies=[Depends(get_current_active_superuser)],
    )
    async def delete_user(
        id: PydanticObjectId,
        request: Request,
    ):
        user = await user_manager.get(id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await user_manager.delete(user, request=request)
        return None

    return router
