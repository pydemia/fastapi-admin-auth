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

    response = test_client.post(
        "/items",
        # headers={"": "application/json"}
        json={"name": "test"},
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    from mainapp.domain.item import models
    Item = models.Item

    item_0 = Item(name="test 0", description="record 0")
    item_1 = Item(name="test 1", description="record 1")
    item_2 = Item(name="test 2", description="record 2")
    item_3 = Item(name="test 3", description="record 3")

    item_a = Item(name="test a", description="record a")
    item_b = Item(name="test b", description="record b")

    items = [
        item_0, item_1, item_2, item_3,
        item_a, item_b,
    ]
    for item in items:
        response = test_client.post(
            "/items",
            # headers={"": "application/json"}
            json=item.model_dump(),
        )

@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(2)
def test_read_item():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/items",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert isinstance(body["data"], list)


    from urllib.parse import quote
    item_name = "test 0"
    encoded_item_name = quote(item_name)
    response = test_client.get(
        "/items",
        params={"name": encoded_item_name},
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["name"] == item_name

    # get `item_id`
    item_id = body["data"]["id"]

    response = test_client.get(
        f"/items/{item_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == item_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(3)
def test_put_item():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # get `item_id`
    from urllib.parse import quote
    item_name = "test 0"
    encoded_item_name = quote(item_name)
    response = test_client.get(
        "/items",
        params={"name": encoded_item_name},
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["name"] == item_name

    item_id = body["data"]["id"]


    new_name = "test-updated"
    response = test_client.put(
        f"/items/{item_id}",
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
@pytest.mark.order(4)
def test_delete_item():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # get `item_id`
    from urllib.parse import quote
    item_name = "test-updated"
    encoded_item_name = quote(item_name)
    response = test_client.get(
        "/items",
        params={"name": encoded_item_name},
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["name"] == item_name

    item_id = body["data"]["id"]

    response = test_client.delete(
        f"/items/{item_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
