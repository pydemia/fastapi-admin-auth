from starlette_admin.contrib.sqla import Admin
from mainapp.core.database import db

# from fastapi import Request, Response
# from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
# from starlette_admin.exceptions import FormValidationError, LoginFailed

from typing import Optional

from starlette.datastructures import URL
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route
from starlette_admin import BaseAdmin
from starlette_admin.auth import (
    AdminUser,
    AuthProvider,
    login_not_required,
)
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware


from mainapp.core.iam.idp import idp, OIDCUser

idp.authorization_uri
idp.public_key

# from authlib.integrations.starlette_client.apps import StarletteOAuth2App
# oauth = OAuth()
# oauth.register(
#     "keycloak",
#     client_id=idp.client_id,
#     client_secret=idp.client_secret,
#     client_kwargs={
#         "scope": "openid profile email",
#     },
#     server_metadata_url=f"{idp.realm_uri}/.well-known/openid-configuration",
#     # access_token_url='https://github.com/login/oauth/access_token',
#     # access_token_params=None,
#     # authorize_url='https://github.com/login/oauth/authorize',
#     # authorize_params=None,
#     # api_base_url='https://api.github.com/',
# )
# oauth: StarletteOAuth2App
from mainapp.core.iam.oauth import oauth_client


class KeycloakAuthProvider(AuthProvider):
    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("user", None) is not None:
            request.state.user = request.session.get("user")
            return True
        return False

    def get_admin_user(self, request: Request) -> Optional[AdminUser]:
        user = request.state.user
        oidc_user: OIDCUser = OIDCUser.model_validate(user)
        return AdminUser(
            username=oidc_user.preferred_username,
        )
        # return AdminUser(
        #     username=user["name"],
        #     photo_url=user["picture"],
        # )


    # async def render_login(self, request: Request, admin: BaseAdmin):
    #     """Override the default login behavior to implement custom logic."""

    #     from fastapi.datastructures import URL
    #     keycloak_login_uri = (
    #         URL(idp.login_uri)
    #         .include_query_params(next=request.query_params.get("next"))
    #     )
    #     return RedirectResponse(keycloak_login_uri)


    async def render_login(self, request: Request, admin: BaseAdmin):
        """Override the default login behavior to implement custom logic."""

        redirect_uri = (
            request
            .url_for(
                admin.route_name + ":authorize_keycloak"
            )
            .include_query_params(next=request.query_params.get("next"))
        )
        return await oauth_client.authorize_redirect(request, str(redirect_uri))


    async def render_logout(self, request: Request, admin: BaseAdmin) -> Response:
        """Override the default logout to implement custom logic"""
        request.session.clear()
        return RedirectResponse(
            url=URL(idp.logout_uri).include_query_params(
                post_logout_redirect_uri=request.url_for(admin.route_name + ":index"),
                client_id=idp.client_id,
            )
        )
        # return RedirectResponse(
        #     url=URL(f"{idp.realm_uri}/v2/logout").include_query_params(
        #         returnTo=request.url_for(admin.route_name + ":index"),
        #         client_id=idp.client_id,
        #     )
        # )

    @login_not_required
    async def handle_auth_callback(self, request: Request):
        token = await oauth_client.authorize_access_token(request)
        request.session.update({"user": token["userinfo"]})
        return RedirectResponse(request.query_params.get("next"))

    def setup_admin(self, admin: "BaseAdmin"):
        # admin.middlewares.append(self.get_middleware(admin=admin))
        # login_route = self.get_login_route(admin=admin)
        # logout_route = self.get_logout_route(admin=admin)
        # login_route.name = "login"
        # logout_route.name = "logout"
        # admin.routes.extend([login_route, logout_route])
        super().setup_admin(admin)
        """add custom authentication callback route"""
        admin.routes
        admin.routes.append(
            Route(
                # "/auth0/authorize",
                # "/dashboard",
                # admin.base_url,
                "/callback",
                self.handle_auth_callback,
                methods=["GET"],
                name="authorize_keycloak",
            )
        )

SECRET = "1234567890"
admin = Admin(
    db.engine,
    title="FastAPI-SQLModel Admin",
    base_url="/dashboard",
    route_name="dashboard",
    statics_dir="mainapp/static/dashboard",
    templates_dir="mainapp/templates/dashboard",
    # logo_url="`https`://preview.tabler.io/static/logo-white.svg",
    # logo_url="statics/logo-fastapi.png",
    logo_url="http://localhost:8000/static/dashboard/logo-fastapi.png",
    login_logo_url="`https`://preview.tabler.io/static/logo.svg",
    # index_view=CustomView(label="Home", icon="fa fa-home", path="/home", template_path="home.html"),
    auth_provider=KeycloakAuthProvider(
        login_path="/sign-in",
        logout_path="/sign-out",
    ),
    middlewares=[Middleware(SessionMiddleware, secret_key=SECRET)],
    # middlewares=[Middleware(SessionMiddleware)],
    debug=True,
    # i18n_config = I18nConfig(default_locale="en")
)
