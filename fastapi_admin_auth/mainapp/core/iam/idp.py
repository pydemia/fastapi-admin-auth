from functools import lru_cache
from mainapp.core.config import KeycloakConfig
from fastapi import Request

from fastapi_keycloak import FastAPIKeycloak
from fastapi_keycloak import OIDCUser
from mainapp.core.types.exceptions import HandledException, ResponseCode


# @logged
# class IDProvider:
#     def __init__(
#         self,
#         keycloak_config: KeycloakConfig,
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

# # idp = IDProvider(core_config.KeycloakConfig())
keycloak_config = KeycloakConfig()

@lru_cache
def get_idp() -> FastAPIKeycloak:
    try:
        idp = FastAPIKeycloak(
            server_url=keycloak_config.server_url,
            client_id=keycloak_config.client_id,
            client_secret=keycloak_config.client_secret,
            admin_client_id=keycloak_config.admin_client_id,
            admin_client_secret=keycloak_config.admin_client_secret,
            realm=keycloak_config.realm,
            callback_uri=keycloak_config.callback_uri,
            scope="openid profile email",
            timeout=10,
        )
    except "requests.exceptions.MissingSchema" as schema_e:
        raise HandledException(ResponseCode.KEYCLOCK_REALM_NOT_FOUND, e=schema_e)
    except "http.client.RemoteDisconnected" as disconnected_e:
        raise HandledException(ResponseCode.KEYCLOCK_CONNECTION_ERROR, e=disconnected_e)
    except Exception as unknown_e:
        raise HandledException(ResponseCode.KEYCLOCK_CONNECTION_ERROR, e=unknown_e)
    return idp

idp = get_idp()
User = OIDCUser

def get_user_id(request: Request) -> str | None:
    return request.state.user.get("sub")

