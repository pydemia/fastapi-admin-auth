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
def test_create_item():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # Create by json
    item_body = {
        "name": "test",
        "description": "test_desc",
    }
    response = test_client.post(
        "/example/items",
        json=item_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


    # Create by Model
    from mainapp.domains.example.item.models import Item

    item_0 = Item(name="item 0", description="item_0")
    item_1 = Item(name="item 1", description="item_1")
    item_2 = Item(name="item 2", description="item_2")
    item_3 = Item(name="item 3", description="item_3")

    items = [
        item_0, item_1, item_2, item_3,
    ]
    for item in items:
        response = test_client.post(
            "/example/items",
            json=item.model_dump(),
        )


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(2)
def test_read_items_all():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/example/items",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert isinstance(body["data"], list)


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(3)
def test_read_item_by_param():

    from fastapi.testclient import TestClient
    from mainapp.main import app

    test_client = TestClient(app)


    item_body = {
        "name": "test",
        "description": "test_desc",
    }
    item_name = item_body["name"]

    from urllib.parse import quote
    encoded_item_name = quote(item_name)

    response = test_client.get(
        "/example/items",
        params={
            "name": encoded_item_name,
        },
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["name"] == item_name

@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_item_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/example/items",
    )
    item_body = response.json()["data"][0]
    item_id = item_body["id"]


    response = test_client.get(
        f"/example/items/{item_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == item_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(5)
def test_put_item():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/example/items",
    )
    item_body = response.json()["data"][0]
    item_id = item_body["id"]


    new_name = "test-updated"
    response = test_client.put(
        f"/example/items/{item_id}",
        json={
            "name": new_name,
            "description": "updated",
        }
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == item_id
    assert body["data"]["name"] == new_name


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(6)
def test_delete_item():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/example/items",
    )
    item_body = response.json()["data"][0]
    item_id = item_body["id"]


    response = test_client.delete(
        f"/example/items/{item_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
