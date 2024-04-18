from authlib.integrations.starlette_client import (
    OAuth,
    StarletteOAuth2App,
)
# from authlib.integrations.starlette_client.apps import StarletteOAuth2App
# from authlib.integrations.httpx_client.oauth2_client import AsyncOAuth2Client
from mainapp.core.iam.idp import idp


oauth: OAuth = OAuth()
oauth.register(
    "keycloak",
    client_id=idp.client_id,
    client_secret=idp.client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"{idp.realm_uri}/.well-known/openid-configuration",
    # authorize_url
)

oauth_client: StarletteOAuth2App = oauth.create_client("keycloak")

# oauth_client.client_cls: AsyncOAuth2Client