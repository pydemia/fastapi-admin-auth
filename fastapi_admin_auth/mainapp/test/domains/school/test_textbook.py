import pytest



@pytest.fixture()
def setup():
    # code to tear down test environm
    pass


@pytest.fixture()
def teardown():
    # code to tear down test environment
    pass


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(1)
def test_create_textbook():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # Create by json
    textbook_body = {
        "name": "test",
        "description": "test_desc",
    }
    response = test_client.post(
        "/school/textbooks",
        json=textbook_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


    # Create by Model
    from mainapp.domains.school.textbook.models import Textbook

    textbook_1 = Textbook(name="textbook test1", description="textbook_test1")
    textbook_2 = Textbook(name="textbook test2", description="textbook_test2")
    textbook_3 = Textbook(name="textbook test3", description="textbook_test3")
    textbook_4 = Textbook(name="textbook test0", description="textbook_test0")

    textbooks = [
        textbook_1, textbook_2, textbook_3, textbook_4,
    ]
    for textbook in textbooks:
        response = test_client.post(
            "/school/textbooks",
            json=textbook.model_dump(),
        )


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(2)
def test_read_textbooks_all():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/textbooks",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert isinstance(body["data"], list)


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(3)
def test_read_textbook_by_param():

    from fastapi.testclient import TestClient
    from mainapp.main import app

    test_client = TestClient(app)


    textbook_body = {
        "name": "test",
        "description": "test_desc",
    }
    textbook_name = textbook_body["name"]

    from urllib.parse import quote
    encoded_textbook_name = quote(textbook_name)

    response = test_client.get(
        "/school/textbooks",
        params={
            "name": encoded_textbook_name,
        },
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"][0]
    assert d["name"] == textbook_name

@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_textbook_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/textbooks",
    )
    textbook = response.json()["data"][0]
    textbook_id = textbook["id"]


    response = test_client.get(
        f"/school/textbooks/{textbook_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"]
    assert d["id"] == textbook_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(5)
def test_put_textbook():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    textbook_body = {
        "name": "test",
        "description": "test_desc",
    }
    textbook_name = textbook_body["name"]

    from urllib.parse import quote
    encoded_textbook_name = quote(textbook_name)

    response = test_client.get(
        "/school/textbooks",
        params={
            "name": encoded_textbook_name,
        },
    )
    textbook = response.json()["data"][0]
    textbook_id = textbook["id"]


    new_name = "test-updated"
    new_desc = "updated"

    response = test_client.put(
        f"/school/textbooks/{textbook_id}",
        json={
            "name": new_name,
            "description": new_desc,
        }
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"]
    assert d["id"] == textbook_id
    assert d["name"] == new_name


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(6)
def test_delete_textbook():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    textbook_body = {
        "name": "test-updated",
        "description": "updated",
    }
    textbook_name = textbook_body["name"]

    from urllib.parse import quote
    encoded_textbook_name = quote(textbook_name)

    response = test_client.get(
        "/school/textbooks",
        params={
            "name": encoded_textbook_name,
        },
    )
    textbook = response.json()["data"][0]
    textbook_id = textbook["id"]


    response = test_client.delete(
        f"/school/textbooks/{textbook_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
