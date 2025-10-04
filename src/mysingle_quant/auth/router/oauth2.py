from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2Token

from ..exceptions import AuthenticationFailed
from ..oauth2.clients import get_oauth2_client
from ..schemas import OAuth2AuthorizeResponse, UserResponse
from ..user_manager import UserManager

user_manager = UserManager()


def get_oauth2_router(
    provider_name: Literal["google", "kakao", "naver"] = "google",
    redirect_url: str | None = None,
) -> APIRouter:
    """Generate a router with the OAuth routes to associate an authenticated user."""

    router = APIRouter()

    oauth_client = get_oauth2_client(provider_name=provider_name)
    callback_route_name = f"{provider_name}.callback"

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
        response_model=OAuth2AuthorizeResponse,
    )
    async def authorize(
        request: Request,
        state: str | None = Query(None),
        scopes: list[str] = Query(None),
    ) -> OAuth2AuthorizeResponse:
        """
        Initiate the OAuth2 authorization process for associating an OAuth account
        with the currently authenticated user.
        """
        if redirect_url is not None:
            authorize_redirect_url = redirect_url
        else:
            authorize_redirect_url = str(request.url_for(callback_route_name))

        authorization_url = await oauth_client.get_authorization_url(
            redirect_uri=authorize_redirect_url,
            state=state,
            scope=scopes,
            code_challenge=None,
            code_challenge_method=None,
            extras_params={},
        )

        return OAuth2AuthorizeResponse(authorization_url=authorization_url)

    @router.get(
        "/{provider}/callback",
        response_model=UserResponse,
        description="The response varies based on the authentication backend used.",
    )
    async def callback(
        request: Request,
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

        # try:
        #     state_data = decode_jwt(token=state, audience="users:oauth-state")
        # except jwt.DecodeError:
        #     raise AuthenticationFailed("Invalid OAuth state token")

        user = await user_manager.oauth_callback(
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
