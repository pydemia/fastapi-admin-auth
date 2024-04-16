from typing import List, Optional
from fastapi import Depends, Query, Body, APIRouter
from pydantic import SecretStr
from dependency_injector.wiring import inject, Provide
from mainapp.core.dependencies import Container
from fastapi_keycloak import FastAPIKeycloak, OIDCUser, UsernamePassword, HTTPMethod, KeycloakUser

from mainapp.core.exception_routers import HandledExceptionLoggingRoute



# @logged
# @inject
# class IDProvider:
#     def __init__(
#         self,
#         keycloak_config = Provide[Container.keycloak_config],
#     ) -> None:
#         self.config = keycloak_config
#         self.client = FastAPIKeycloak(
#             server_url=self.config.server_url,
#             client_id=self.config.client_id,
#             client_secret=self.config.client_secret,
#             admin_client_id=self.config.admin_client_id,
#             admin_client_secret=self.config.admin_client_secret,
#             realm=self.config.realm,
#             callback_uri=self.config.callback_uri,
#         )
#     def add_app(self, app: FastAPI) -> FastAPI:
#         self.client.add_swagger_config(app)
#         return app

# @inject
# def get_idp(config = Provide["keycloak_config"]):
#     idp = FastAPIKeycloak(
#         server_url=config.server_url,
#         client_id=config.client_id,
#         client_secret=config.client_secret,
#         admin_client_id=config.admin_client_id,
#         admin_client_secret=config.admin_client_secret,
#         realm=config.realm,
#         callback_uri=config.callback_uri,
#     )
#     return idp


# from fastapi import FastAPI
# @inject
# def add_swagger_config(
#     app: FastAPI,
#     # idp: FastAPIKeycloak = Provide["idp"],
#     idp: FastAPIKeycloak
# ) -> FastAPI:
#     idp.add_swagger_config(app)
#     return app
# idp = FastAPIKeycloak(
#     server_url="http://localhost:10000",
#     client_id="fastapi-admin-auth-app",
#     client_secret="iRJRjyNKZ3zqbwW3NXHJLhTgbMT20SPM",
#     admin_client_id="admin-cli",
#     admin_client_secret="WJmdud32rsQ4TzbPuGiU1V6pPWhOH8pq",
#     realm="fastapi-admin-auth",
#     callback_uri="http://localhost:8000/callback"
# )

# def add_swagger_config(app: FastAPI) -> FastAPI:
#     idp.add_swagger_config(app)
#     return app

# from fastapi import FastAPI
# from mainapp.core.config import KeycloakConfig
# @inject
# def get_idp(config: KeycloakConfig = Provide["keycloak_config"]):
#     idp = FastAPIKeycloak(
#         server_url=config.server_url,
#         client_id=config.client_id,
#         client_secret=config.client_secret,
#         admin_client_id=config.admin_client_id,
#         admin_client_secret=config.admin_client_secret,
#         realm=config.realm,
#         callback_uri=config.callback_uri,
#     )
#     return idp

# @inject
# def add_swagger_config(
#     app: FastAPI,
#     idp: FastAPIKeycloak = Provide["idp"],
# ) -> FastAPI:
#     idp.add_swagger_config(app)
#     return app
from .idp import idp, get_idp

router = APIRouter(
    prefix="/iam",
    route_class=HandledExceptionLoggingRoute,
)

# Admin
admin_router = APIRouter(
    tags=["iam/admin"],
    route_class=HandledExceptionLoggingRoute,
)

@admin_router.post("/proxy")
@inject
async def proxy_admin_request(
    relative_path: str,
    method: HTTPMethod,
    additional_headers: dict = Body(None),
    payload: dict = Body(None),
    idp: FastAPIKeycloak = Depends(get_idp),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
):
    return idp.proxy(
        additional_headers=additional_headers,
        relative_path=relative_path,
        method=method,
        payload=payload
    )

@admin_router.get("/identity-providers")
@inject
async def get_identity_providers(
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_identity_providers()

@admin_router.get("/idp-configuration")
@inject
async def get_idp_config(
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.open_id_configuration

@admin_router.get("/callback")
@inject
async def callback(
    session_state: str,
    code: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.exchange_authorization_code(session_state=session_state, code=code)

router.include_router(admin_router)


# User Management
users_router = APIRouter(
    tags=["iam/users"],
    route_class=HandledExceptionLoggingRoute,
)

@users_router.get("/users")
@inject
async def get_users(
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_all_users()


@users_router.get("/user")
@inject
async def get_user_by_query(
    query: str = None,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_user(query=query)


@users_router.post("/users")
@inject
async def create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: SecretStr,
    id: str = None,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.create_user(
        first_name=first_name,
        last_name=last_name,
        username=email,
        email=email,
        password=password.get_secret_value(),
        id=id
    )


@users_router.get("/user/{user_id}")
@inject
async def get_user(
    user_id: str = None,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_user(user_id=user_id)


@users_router.put("/user")
@inject
async def update_user(
    user: KeycloakUser,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.update_user(user=user)


@users_router.delete("/user/{user_id}")
@inject
async def delete_user(
    user_id: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.delete_user(user_id=user_id)


@users_router.put("/user/{user_id}/change-password")
@inject
async def change_password(
    user_id: str,
    new_password: SecretStr,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.change_password(user_id=user_id, new_password=new_password)


@users_router.put("/user/{user_id}/send-email-verification")
@inject
async def send_email_verification(
    user_id: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.send_email_verification(user_id=user_id)

router.include_router(users_router)


# Role Management
roles_router = APIRouter(
    tags=["iam/roles"],
    route_class=HandledExceptionLoggingRoute,
)

@roles_router.get("/roles")
@inject
async def get_all_roles(
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_all_roles()


@roles_router.get("/role/{role_name}")
@inject
async def get_role(
    role_name: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_roles([role_name])


@roles_router.post("/roles")
@inject
async def add_role(
    role_name: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.create_role(role_name=role_name)


@roles_router.delete("/roles")
@inject
async def delete_roles(
    role_name: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.delete_role(role_name=role_name)

router.include_router(roles_router)


# Group Management
groups_router = APIRouter(
    tags=["iam/groups"],
    route_class=HandledExceptionLoggingRoute,
)


@groups_router.get("/groups")
@inject
async def get_all_groups(
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_all_groups()


@groups_router.get("/group/{group_name}")
@inject
async def get_group(
    group_name: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_groups([group_name])


@groups_router.get("/group-by-path/{path: path}")
@inject
async def get_group_by_path(
    path: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_group_by_path(path)


@groups_router.post("/groups")
@inject
async def add_group(
    group_name: str,
    parent_id: Optional[str] = None,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.create_group(group_name=group_name, parent=parent_id)


@groups_router.delete("/groups")
@inject
async def delete_groups(
    group_id: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.delete_group(group_id=group_id)

router.include_router(groups_router)


# User Roles
user_roles_router = APIRouter(
    tags=["iam/user-roles"],
    route_class=HandledExceptionLoggingRoute,
)

@user_roles_router.post("/users/{user_id}/roles")
@inject
async def add_roles_to_user(
    user_id: str,
    roles: Optional[List[str]] = Query(None),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.add_user_roles(user_id=user_id, roles=roles)


@user_roles_router.get("/users/{user_id}/roles")
@inject
async def get_user_roles(
    user_id: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_user_roles(user_id=user_id)


@user_roles_router.delete("/users/{user_id}/roles")
@inject
async def delete_roles_from_user(
    user_id: str,
    roles: Optional[List[str]] = Query(None),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.remove_user_roles(user_id=user_id, roles=roles)

router.include_router(user_roles_router)

# User Groups
user_groups_router = APIRouter(tags=["iam/user-groups"])

@user_groups_router.post("/users/{user_id}/groups")
@inject
async def add_group_to_user(
    user_id: str,
    group_id: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.add_user_group(user_id=user_id, group_id=group_id)


@user_groups_router.get("/users/{user_id}/groups")
@inject
async def get_user_groups(
    user_id: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.get_user_groups(user_id=user_id)


@user_groups_router.delete("/users/{user_id}/groups")
@inject
async def delete_groups_from_user(
    user_id: str,
    group_id: str,
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.remove_user_group(user_id=user_id, group_id=group_id)

router.include_router(user_groups_router)


# Example User Requests
example_user_requests_router = APIRouter(
    tags=["iam/example-user-requests"],
    route_class=HandledExceptionLoggingRoute,
)

# @inject
# def idp_get_current_user(
#     idp: FastAPIKeycloak = Provide[Container.idp],
# ):
#     return idp.get_current_user

@example_user_requests_router.get("/protected")
@inject
async def protected(
    user: OIDCUser = Depends(idp.get_current_user()),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return user

# from .idp import IDProvider
# idp = IDProvider()

@example_user_requests_router.get("/current_user/roles")
@inject
async def get_current_users_roles(
    user: OIDCUser = Depends(idp.get_current_user()),
    # user: OIDCUser = Depends(Provide[Container.idp.provided.get_current_user()]),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
    ):
    return user.roles


@example_user_requests_router.get("/require_admin")
@inject
async def require_admin_role(
    user: OIDCUser = Depends(idp.get_current_user(required_roles=["admin"])),
    # user: OIDCUser = Depends(Provide[Container.idp.provided.get_current_user(required_roles=["admin"])]),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return f'Hi admin {user}'


@example_user_requests_router.get("/login")
@inject
async def login(
    user: UsernamePassword = Depends(),
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.user_login(
        username=user.username,
        password=user.password.get_secret_value()
    )

@example_user_requests_router.get("/login-link")
@inject
async def login_redirect(
    # idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
    idp: FastAPIKeycloak = Depends(get_idp),
):
    return idp.login_uri

@example_user_requests_router.get("/logout")
@inject
async def logout(
    idp: FastAPIKeycloak = Depends(Provide[Container.idp]),
):
    return idp.logout_uri

router.include_router(example_user_requests_router)
