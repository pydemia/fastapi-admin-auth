from typing import List, Optional
from fastapi import FastAPI, Depends, Query, Body, APIRouter
from pydantic import SecretStr
from fastapi_keycloak import FastAPIKeycloak, OIDCUser, UsernamePassword, HTTPMethod, KeycloakUser

from mainapp.core.exception_routers import HandledExceptionLoggingRoute


idp = FastAPIKeycloak(
    server_url="http://localhost:10000",
    client_id="fastapi-admin-auth-app",
    client_secret="iRJRjyNKZ3zqbwW3NXHJLhTgbMT20SPM",
    admin_client_id="admin-cli",
    admin_client_secret="WJmdud32rsQ4TzbPuGiU1V6pPWhOH8pq",
    realm="fastapi-admin-auth",
    callback_uri="http://localhost:8000/callback"
)

def add_swagger_config(app: FastAPI) -> FastAPI:
    idp.add_swagger_config(app)
    return app

router = APIRouter(
    prefix="/iam",
    route_class=HandledExceptionLoggingRoute,
)

# Admin
admin_router = APIRouter(tags=["iam/admin"])

@admin_router.post("/proxy")
def proxy_admin_request(relative_path: str, method: HTTPMethod, additional_headers: dict = Body(None), payload: dict = Body(None)):
    return idp.proxy(
        additional_headers=additional_headers,
        relative_path=relative_path,
        method=method,
        payload=payload
    )

@admin_router.get("/identity-providers")
def get_identity_providers():
    return idp.get_identity_providers()

@admin_router.get("/idp-configuration")
def get_idp_config():
    return idp.open_id_configuration

@admin_router.get("/callback")
def callback(session_state: str, code: str):
    return idp.exchange_authorization_code(session_state=session_state, code=code)

router.include_router(admin_router)


# User Management
users_router = APIRouter(tags=["iam/users"])

@users_router.get("/users")
def get_users():
    return idp.get_all_users()


@users_router.get("/user")
def get_user_by_query(query: str = None):
    return idp.get_user(query=query)


@users_router.post("/users")
def create_user(first_name: str, last_name: str, email: str, password: SecretStr, id: str = None):
    return idp.create_user(
        first_name=first_name,
        last_name=last_name,
        username=email,
        email=email,
        password=password.get_secret_value(),
        id=id
    )


@users_router.get("/user/{user_id}")
def get_user(user_id: str = None):
    return idp.get_user(user_id=user_id)


@users_router.put("/user")
def update_user(user: KeycloakUser):
    return idp.update_user(user=user)


@users_router.delete("/user/{user_id}")
def delete_user(user_id: str):
    return idp.delete_user(user_id=user_id)


@users_router.put("/user/{user_id}/change-password")
def change_password(user_id: str, new_password: SecretStr):
    return idp.change_password(user_id=user_id, new_password=new_password)


@users_router.put("/user/{user_id}/send-email-verification")
def send_email_verification(user_id: str):
    return idp.send_email_verification(user_id=user_id)

router.include_router(users_router)


# Role Management
roles_router = APIRouter(tags=["iam/roles"])

@roles_router.get("/roles")
def get_all_roles():
    return idp.get_all_roles()


@roles_router.get("/role/{role_name}")
def get_role(role_name: str):
    return idp.get_roles([role_name])


@roles_router.post("/roles")
def add_role(role_name: str):
    return idp.create_role(role_name=role_name)


@roles_router.delete("/roles")
def delete_roles(role_name: str):
    return idp.delete_role(role_name=role_name)

router.include_router(roles_router)


# Group Management
groups_router = APIRouter(tags=["iam/groups"])


@groups_router.get("/groups")
def get_all_groups():
    return idp.get_all_groups()


@groups_router.get("/group/{group_name}")
def get_group(group_name: str):
    return idp.get_groups([group_name])


@groups_router.get("/group-by-path/{path: path}")
def get_group_by_path(path: str):
    return idp.get_group_by_path(path)


@groups_router.post("/groups")
def add_group(group_name: str, parent_id: Optional[str] = None):
    return idp.create_group(group_name=group_name, parent=parent_id)


@groups_router.delete("/groups")
def delete_groups(group_id: str):
    return idp.delete_group(group_id=group_id)

router.include_router(groups_router)


# User Roles
user_roles_router = APIRouter(tags=["iam/user-roles"])

@user_roles_router.post("/users/{user_id}/roles")
def add_roles_to_user(user_id: str, roles: Optional[List[str]] = Query(None)):
    return idp.add_user_roles(user_id=user_id, roles=roles)


@user_roles_router.get("/users/{user_id}/roles")
def get_user_roles(user_id: str):
    return idp.get_user_roles(user_id=user_id)


@user_roles_router.delete("/users/{user_id}/roles")
def delete_roles_from_user(user_id: str, roles: Optional[List[str]] = Query(None)):
    return idp.remove_user_roles(user_id=user_id, roles=roles)

router.include_router(user_roles_router)

# User Groups
user_groups_router = APIRouter(tags=["iam/user-groups"])

@user_groups_router.post("/users/{user_id}/groups")
def add_group_to_user(user_id: str, group_id: str):
    return idp.add_user_group(user_id=user_id, group_id=group_id)


@user_groups_router.get("/users/{user_id}/groups")
def get_user_groups(user_id: str):
    return idp.get_user_groups(user_id=user_id)


@user_groups_router.delete("/users/{user_id}/groups")
def delete_groups_from_user(user_id: str, group_id: str):
    return idp.remove_user_group(user_id=user_id, group_id=group_id)

router.include_router(user_groups_router)


# Example User Requests
example_user_requests_router = APIRouter(tags=["iam/example-user-requests"])

@example_user_requests_router.get("/protected")
def protected(user: OIDCUser = Depends(idp.get_current_user())):
    return user


@example_user_requests_router.get("/current_user/roles")
def get_current_users_roles(user: OIDCUser = Depends(idp.get_current_user())):
    return user.roles


@example_user_requests_router.get("/require_admin")
def require_admin_role(user: OIDCUser = Depends(idp.get_current_user(required_roles=["admin"]))):
    return f'Hi admin {user}'


@example_user_requests_router.get("/login")
def login(user: UsernamePassword = Depends()):
    return idp.user_login(
        username=user.username,
        password=user.password.get_secret_value()
    )

@example_user_requests_router.get("/login-link")
def login_redirect():
    return idp.login_uri

@example_user_requests_router.get("/logout")
def logout():
    return idp.logout_uri

router.include_router(example_user_requests_router)
