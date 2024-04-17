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
def test_create_app():
    from mainapp.main import create_app

    create_app
    pass
