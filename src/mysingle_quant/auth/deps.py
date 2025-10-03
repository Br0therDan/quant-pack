# path: app/api/deps.py

import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ..core.config import settings
from .exceptions import (
    AuthorizationFailed,
    UserInactive,
    UserNotExists,
)
from .models import User
from .user_manager import UserManager

logger = logging.getLogger(__name__)

# --------------------------------------------------------
# 패스워드 기반 인증을 위한 OAuth2 설정
# --------------------------------------------------------
VERSION = settings.AUTH_API_VERSION

user_manager = UserManager()
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/{VERSION}/auth/login", auto_error=False
)


async def get_current_user(
    token: str = Depends(reusable_oauth2),
) -> User:
    """
    토큰(쿠키 또는 헤더)을 디코딩하여 현재 사용자를 반환합니다.
    """
    user = await user_manager.read_token(token, token_audience=["quant-users"])
    if not user:
        raise UserNotExists(identifier="token", identifier_type="authenticated user")
    return user


# --------------------------------------------------------
# 활성 사용자 확인
# --------------------------------------------------------


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    현재 사용자가 활성 사용자인지 확인
    """
    if not current_user.is_active:
        raise UserInactive(user_id=str(current_user.id))
    return current_user


# --------------------------------------------------------
# 이메일 검증된 활성 사용자 확인
# --------------------------------------------------------
def get_current_active_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    현재 사용자가 활성 사용자이고 이메일이 확인된 사용자인지 확인
    """
    if not current_user.is_verified:
        raise AuthorizationFailed(
            "Email verification required", user_id=str(current_user.id)
        )
    return current_user


# --------------------------------------------------------
# 슈퍼유저 권한 검증
# --------------------------------------------------------
def get_current_active_superuser(
    current_user: User = Depends(get_current_active_verified_user),
) -> User:
    """
    현재 사용자가 슈퍼유저인지 검증
    """
    if not current_user.is_superuser:
        raise AuthorizationFailed(
            "Superuser privileges required", user_id=str(current_user.id)
        )
    return current_user
