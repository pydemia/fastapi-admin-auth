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
def test_load_database():

    from mainapp.core.database import db

    db
