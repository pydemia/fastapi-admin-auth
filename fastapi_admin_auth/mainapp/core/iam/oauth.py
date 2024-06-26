from functools import lru_cache
from mainapp.core.config import KeycloakConfig
from fastapi import Request

from fastapi_keycloak import FastAPIKeycloak
from fastapi_keycloak import OIDCUser
from mainapp.core.types.exceptions import HandledException, ResponseCode
from requests.exceptions import MissingSchema
from http.client import RemoteDisconnected

from authlib.integrations.starlette_client import (
    OAuth,
    StarletteOAuth2App,
)


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
            scope=keycloak_config.scope,
            timeout=keycloak_config.timeout,
        )
    except MissingSchema as schema_e:
        raise HandledException(ResponseCode.KEYCLOCK_REALM_NOT_FOUND, e=schema_e)
    except RemoteDisconnected as disconnected_e:
        raise HandledException(ResponseCode.KEYCLOCK_CONNECTION_ERROR, e=disconnected_e)
    except Exception as unknown_e:
        raise HandledException(ResponseCode.KEYCLOCK_CONNECTION_ERROR, e=unknown_e)
    return idp

idp = get_idp()
User = OIDCUser

def get_user_id(request: Request) -> str | None:
    return request.state.user.get("sub")


oauth: OAuth = OAuth()
oauth.register(
    "keycloak",
    client_id=keycloak_config.client_id,
    client_secret=keycloak_config.client_secret,
    client_kwargs={
        "scope": keycloak_config.scope,
        "timeout": keycloak_config.timeout,
    },
    server_metadata_url=f"{idp.realm_uri}/.well-known/openid-configuration",
    # authorize_url
)

oauth_client: StarletteOAuth2App = oauth.create_client("keycloak")
