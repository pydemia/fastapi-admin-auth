from mainapp.core.config import KeycloakConfig

from fastapi_keycloak import FastAPIKeycloak

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
idp = FastAPIKeycloak(
    server_url=keycloak_config.server_url,
    client_id=keycloak_config.client_id,
    client_secret=keycloak_config.client_secret,
    admin_client_id=keycloak_config.admin_client_id,
    admin_client_secret=keycloak_config.admin_client_secret,
    realm=keycloak_config.realm,
    callback_uri=keycloak_config.callback_uri,
)

def get_idp() -> FastAPIKeycloak:
    return idp
