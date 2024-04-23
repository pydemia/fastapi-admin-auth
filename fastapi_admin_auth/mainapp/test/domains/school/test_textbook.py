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
    from mainapp.domains.school.textbook import models
    Textbook = models.Textbook

    textbook_0 = Textbook(name="textbook 0", description="textbook_0")
    textbook_1 = Textbook(name="textbook 1", description="textbook_1")
    textbook_2 = Textbook(name="textbook 2", description="textbook_2")
    textbook_3 = Textbook(name="textbook 3", description="textbook_3")

    textbook_a = Textbook(name="textbook a", description="textbook_a")
    textbook_b = Textbook(name="textbook b", description="textbook_b")

    textbooks = [
        textbook_0, textbook_1, textbook_2, textbook_3,
        textbook_a, textbook_b,
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
    assert body["data"]["name"] == textbook_name

@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_textbook_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/textbooks",
    )
    textbook_body = response.json()["data"][0]
    textbook_id = textbook_body["id"]


    response = test_client.get(
        f"/school/textbooks/{textbook_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == textbook_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(5)
def test_put_textbook():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/textbooks",
    )
    textbook_body = response.json()["data"][0]
    textbook_id = textbook_body["id"]


    new_name = "test-updated"
    response = test_client.put(
        f"/school/textbooks/{textbook_id}",
        json={
            "name": new_name,
            "description": "updated",
        }
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == textbook_id
    assert body["data"]["name"] == new_name


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(6)
def test_delete_textbook():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/textbooks",
    )
    textbook_body = response.json()["data"][0]
    textbook_id = textbook_body["id"]


    response = test_client.delete(
        f"/school/textbooks/{textbook_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
