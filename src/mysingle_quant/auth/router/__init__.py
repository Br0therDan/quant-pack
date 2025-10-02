from fastapi import APIRouter

from .auth import create_auth_router
from .oauth_management import get_oauth_management_router
from .register import get_register_router
from .reset import get_reset_password_router
from .users import get_users_router
from .verify import get_verify_router

auth_router = create_auth_router()
user_router = get_users_router()
oauth_management_router = get_oauth_management_router()
register_router = get_register_router()
reset_password_router = get_reset_password_router()
verify_router = get_verify_router()

auth_router = APIRouter(prefix="/auth", tags=["auth"])

auth_router.include_router(auth_router)
auth_router.include_router(register_router)
auth_router.include_router(reset_password_router)
auth_router.include_router(verify_router)


__all__ = [
    "auth_router",
    "user_router",
]
