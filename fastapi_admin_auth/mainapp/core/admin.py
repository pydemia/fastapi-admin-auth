from starlette_admin.contrib.sqla import Admin
from mainapp.core.database import db

# from fastapi import Request, Response
# from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
# from starlette_admin.exceptions import FormValidationError, LoginFailed

from typing import Optional, Any

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
from starlette.middleware.authentication import AuthenticationMiddleware, AuthenticationBackend
from starlette_admin import CustomView


from starlette_admin.views import BaseView  # for typing: childs: BaseModelView, ModelView, CustomView
from starlette_admin.contrib.sqla import ModelView
from starlette_admin import action, row_action
from mainapp.core.iam.idp import idp, OIDCUser


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
            photo_url="http://localhost:8000/static/dashboard/icon-user.svg",
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
        return await oauth_client.authorize_redirect(request, redirect_uri)


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


# from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
import base64
import binascii
# class BasicAuthBackend(AuthenticationBackend):
#     async def authenticate(self, conn):
#         if "Authorization" not in conn.headers:
#             return

#         auth = conn.headers["Authorization"]
#         try:
#             scheme, credentials = auth.split()
#             if scheme.lower() != 'basic':
#                 return
#             decoded = base64.b64decode(credentials).decode("ascii")
#         except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
#             raise AuthenticationError('Invalid basic auth credentials')

#         username, _, password = decoded.partition(":")
#         # TODO: You'd want to verify the username and password here.
#         return AuthCredentials(["authenticated"]), SimpleUser(username)
class KeycloakAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'basic':
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError('Invalid basic auth credentials')

        username, _, password = decoded.partition(":")
        # TODO: You'd want to verify the username and password here.
        return AuthCredentials(["authenticated"]), SimpleUser(username)



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
    middlewares=[
        Middleware(AuthenticationMiddleware, backend=KeycloakAuthBackend()),
        Middleware(SessionMiddleware, secret_key=""),
    ],
        # MiddleWare(AuthenticationMiddleware, backend=BasicAuthBackend())
    # middlewares=[Middleware(SessionMiddleware)],
    debug=True,
    # i18n_config = I18nConfig(default_locale="en")
)



from fastapi.security import OAuth2PasswordBearer

# OAuth2PasswordBearer()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=idp.token_uri,
    auto_error=False,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=idp.token_uri)
# oauth2_scheme(request.headers["token"])


def get_keycloak_user(request: Request) -> OIDCUser:
    user = request.state.user
    oidc_user: OIDCUser = OIDCUser.model_validate(user)
    return oidc_user

def get_keycloak_user_id(request: Request):
    return request.state.user["sub"]

async def get_keycloak_current_user(request: Request):
    from fastapi.security import OAuth2PasswordBearer

    # OAuth2PasswordBearer()
    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl=idp.token_uri,
        auto_error=False,
    )
    token = await oauth2_scheme(request)
    decoded_token = idp._decode_token(token, audience="account")
    user = OIDCUser.model_validate(decoded_token)
    # if required_roles

# # idp.get_current_user(required_roles=["default-roles-fastapi-admin-auth"])
# # idp.get_current_user(required_roles=[])

# aa = await idp.user_auth_scheme(request)


# def current_user(
#     # token: OAuth2PasswordBearer = Depends(self.user_auth_scheme),
#     token = idp.user_auth_scheme()
# ) -> OIDCUser:
#     """Decodes and verifies a JWT to get the current user

#     Args:
#         token OAuth2PasswordBearer: Access token in `Authorization` HTTP-header

#     Returns:
#         OIDCUser: Decoded JWT content

#     Raises:
#         ExpiredSignatureError: If the token is expired (exp > datetime.now())
#         JWTError: If decoding fails or the signature is invalid
#         JWTClaimsError: If any claim is invalid
#         HTTPException: If any role required is not contained within the roles of the users
#     """
#     decoded_token = self._decode_token(token=token, audience="account")
#     user = OIDCUser.parse_obj(decoded_token)
#     if required_roles:
#         for role in required_roles:
#             if role not in user.roles:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail=f'Role "{role}" is required to perform this action',
#                 )

#     if extra_fields:
#         for field in extra_fields:
#             user.extra_fields[field] = decoded_token.get(field, None)

#     return user

# from fastapi import Depends
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import (
    get_dependant,
    solve_dependencies
)

Dependant
get_dependant
solve_dependencies


class AuthorizedModelView(CustomView):
    def is_accessible(
            self, request: Request,
            # user: OIDCUser = Depends(idp.get_current_user()),
        ) -> bool:
        return True
        # uu = request.state.user
        # roles = request.state.user.get("roles")
        # if roles is None:
        #     return False
        # if "default-roles-fastapi-admin-auth" not in roles:
        #     return False
        # # key = request.state.user
        # return True
    




class CustomActionedSampleModelView(ModelView):
    # exclude_fields_from_list = [Item.body]

    def can_view_details(self, request: Request) -> bool:
        return "read" in request.state.user["roles"]

    def can_create(self, request: Request) -> bool:
        return "create" in request.state.user["roles"]

    def can_edit(self, request: Request) -> bool:
        return "edit" in request.state.user["roles"]

    def can_delete(self, request: Request) -> bool:
        return "delete" in request.state.user["roles"]

    async def is_action_allowed(self, request: Request, name: str) -> bool:
        if name == "make_published":
            return "action_make_published" in request.state.user["roles"]
        return await super().is_action_allowed(request, name)

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        if name == "make_published":
            return "row_action_make_published" in request.state.user["roles"]
        return await super().is_row_action_allowed(request, name)

    @action(
        name="make_published",
        text="Mark selected articles as published",
        confirmation="Are you sure you want to mark selected articles as published ?",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
    )
    async def make_published_action(self, request: Request, pks: list[Any]) -> str:
        ...
        return "{} articles were successfully marked as published".format(len(pks))


    @row_action(
        name="make_published",
        text="Mark as published",
        confirmation="Are you sure you want to mark this article as published ?",
        icon_class="fas fa-check-circle",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-info",
    )
    async def make_published_row_action(self, request: Request, pk: Any) -> str:
        ...
        return "The article was successfully marked as published"


def add_admin_views(
    admin: Admin,
    admin_views: list[BaseView],
) -> Admin:
    for admin_view in admin_views:
        admin.add_view(admin_view)
    return admin
