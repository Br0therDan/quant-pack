from fastapi import APIRouter

from .auth import create_auth_router
from .oauth2 import get_oauth2_router

# from .oauth2 import get_oauth_associate_router
from .oauth_management import get_oauth_management_router
from .register import get_register_router
from .reset import get_reset_password_router
from .users import get_users_router
from .verify import get_verify_router

auth_router = APIRouter()

auth_router.include_router(create_auth_router())
auth_router.include_router(get_register_router())
auth_router.include_router(get_reset_password_router())
auth_router.include_router(get_verify_router())

oauth2_router = APIRouter()

auth_router.include_router(get_oauth2_router(provider_name="google", redirect_url=None))
auth_router.include_router(get_oauth_management_router())

user_router = APIRouter()

user_router.include_router(get_users_router())
user_router.include_router(get_oauth_management_router())

__all__ = ["auth_router", "user_router", "oauth2_router"]
