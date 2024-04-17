import pytest



@pytest.fixture()
def setup():
    # code to tear down test environment
    pass


@pytest.fixture()
def teardown():
    # code to tear down test environment
    pass

@pytest.mark.usefixtures("setup", "teardown")
def test_load_config():

    import os
    from mainapp.core.config import (
        AppConfig,
        DBConfig,
        KeycloakConfig,
    )

    app_config = AppConfig()
    db_config = DBConfig()
    keycloak_config = KeycloakConfig()

    assert os.getenv("APP__VERSION", "1.0.0") == app_config.version

    assert os.getenv("DATABASE__HOST") == db_config.host

    from urllib.parse import urlparse
    url = urlparse(keycloak_config.server_url)
    assert os.getenv("KEYCLOAK__HOST") == f'{url.scheme}://{url.hostname}'
    assert os.getenv("KEYCLOAK__PORT") == str(url.port)
