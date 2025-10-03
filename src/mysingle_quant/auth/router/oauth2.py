import jwt
from fastapi import APIRouter, Depends, Query, Request
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token

from ..deps import get_current_active_user
from ..exceptions import AuthenticationFailed, AuthorizationFailed
from ..models import User
from ..schemas import OAuth2AuthorizeResponse, UserResponse
from ..security import decode_jwt, generate_jwt
from ..user_manager import UserManager

STATE_TOKEN_AUDIENCE = "quant-users:oauth-state"
user_manager = UserManager()


def generate_state_token(data: dict[str, str], lifetime_seconds: int = 3600) -> str:
    data["aud"] = STATE_TOKEN_AUDIENCE
    return generate_jwt(data, lifetime_seconds)


def get_oauth_associate_router(
    oauth_client: BaseOAuth2,
    redirect_url: str | None = None,
) -> APIRouter:
    """Generate a router with the OAuth routes to associate an authenticated user."""
    router = APIRouter()

    callback_route_name = f"oauth-associate:{oauth_client.name}.callback"

    if redirect_url is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            redirect_url=redirect_url,
        )
    else:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            route_name=callback_route_name,
        )

    @router.get(
        "/authorize",
        name=f"oauth-associate:{oauth_client.name}.authorize",
        response_model=OAuth2AuthorizeResponse,
    )
    async def authorize(
        request: Request,
        scopes: list[str] = Query(None),
        user: User = Depends(get_current_active_user),
    ) -> OAuth2AuthorizeResponse:
        if redirect_url is not None:
            authorize_redirect_url = redirect_url
        else:
            authorize_redirect_url = str(request.url_for(callback_route_name))

        state_data: dict[str, str] = {"sub": str(user.id)}
        state = generate_state_token(state_data)
        authorization_url = await oauth_client.get_authorization_url(
            authorize_redirect_url,
            state,
            scopes,
        )

        return OAuth2AuthorizeResponse(authorization_url=authorization_url)

    @router.get(
        "/callback",
        response_model=UserResponse,
        description="The response varies based on the authentication backend used.",
    )
    async def callback(
        request: Request,
        user: User = Depends(get_current_active_user),
        access_token_state: tuple[OAuth2Token, str] = Depends(
            oauth2_authorize_callback
        ),
    ) -> UserResponse:
        token, state = access_token_state
        account_id, account_email = await oauth_client.get_id_email(
            token["access_token"]
        )

        if account_email is None:
            raise AuthenticationFailed("OAuth provider did not provide email")

        try:
            state_data = decode_jwt(state, [STATE_TOKEN_AUDIENCE])
        except jwt.DecodeError:
            raise AuthenticationFailed("Invalid OAuth state token")

        if state_data["sub"] != str(user.id):
            raise AuthorizationFailed("OAuth state user mismatch")

        user = await user_manager.oauth_associate_callback(
            user,
            oauth_client.name,
            token["access_token"],
            account_id,
            account_email,
            token.get("expires_at"),
            token.get("refresh_token"),
            request,
        )

        return UserResponse.model_validate(user, from_attributes=True)

    return router
