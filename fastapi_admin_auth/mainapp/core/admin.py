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



from authlib.integrations.starlette_client import OAuth
from mainapp.core.iam.idp import idp

idp.authorization_uri
idp.public_key


oauth = OAuth()
oauth.register(
    "auth0",
    client_id=idp.client_id,
    client_secret=idp.client_secret,
    # client_kwargs={
    #     "scope": "openid profile email",
    # },
    server_metadata_url=f"https://{idp.realm_uri}/.well-known/openid-configuration",
)

class IDPAuthProvider(AuthProvider):
    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("user", None) is not None:
            request.state.user = request.session.get("user")
            return True
        return False

    def get_admin_user(self, request: Request) -> Optional[AdminUser]:
        user = request.state.user
        return AdminUser(
            username=user["name"],
            photo_url=user["picture"],
        )

    async def render_login(self, request: Request, admin: BaseAdmin):
        """Override the default login behavior to implement custom logic."""
        auth0 = oauth.create_client("auth0")
        redirect_uri = request.url_for(
            admin.route_name + ":authorize_auth0"
        ).include_query_params(next=request.query_params.get("next"))
        return await auth0.authorize_redirect(request, str(redirect_uri))

    async def render_logout(self, request: Request, admin: BaseAdmin) -> Response:
        """Override the default logout to implement custom logic"""
        request.session.clear()
        return RedirectResponse(
            url=URL(f"https://{idp.realm_uri}/v2/logout").include_query_params(
                returnTo=request.url_for(admin.route_name + ":index"),
                client_id=idp.client_id,
            )
        )

    @login_not_required
    async def handle_auth_callback(self, request: Request):
        auth0 = oauth.create_client("auth0")
        token = await auth0.authorize_access_token(request)
        request.session.update({"user": token["userinfo"]})
        return RedirectResponse(request.query_params.get("next"))

    def setup_admin(self, admin: "BaseAdmin"):
        super().setup_admin(admin)
        """add custom authentication callback route"""
        admin.routes.append(
            Route(
                "/auth0/authorize",
                self.handle_auth_callback,
                methods=["GET"],
                name="authorize_auth0",
            )
        )

SECRET = "1234567890"
admin = Admin(
    db.engine,
    title="FastAPI-SQLModel Admin",
    base_url="/dashboard",
    # route_name="dashboard",
    statics_dir="mainapp/static/dashboard",
    templates_dir="mainapp/templates/dashboard",
    logo_url="`https`://preview.tabler.io/static/logo-white.svg",
    login_logo_url="`https`://preview.tabler.io/static/logo.svg",
    # index_view=CustomView(label="Home", icon="fa fa-home", path="/home", template_path="home.html"),
    auth_provider=IDPAuthProvider(
        login_path="/sign-in",
        logout_path="/sign-out",
    ),
    middlewares=[Middleware(SessionMiddleware, secret_key=SECRET)],
    # middlewares=[Middleware(SessionMiddleware)],
    debug=True,
    # i18n_config = I18nConfig(default_locale="en")
)
