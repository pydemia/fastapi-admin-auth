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
def test_create_teacher():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # Create by json
    teacher_body = {
        "firstname": "Richard",
        "lastname": "Roe",
    }

    response = test_client.post(
        "/school/teachers",
        json=teacher_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


    # Create by Model
    from mainapp.domains.school.teacher.models import Teacher

    teacher_1 = Teacher(firstname="Amelia", lastname="Rose", description="teacher test1")
    teacher_2 = Teacher(firstname="Oliver", lastname="Brown", description="teacher test2")
    teacher_3 = Teacher(firstname="Riley", lastname="Sanders", description="teacher test3")
    teacher_4 = Teacher(firstname="Daniel", lastname="Walker", description="teacher test4")

    teachers = [
        teacher_1, teacher_2, teacher_3, teacher_4,
    ]
    for teacher in teachers:
        response = test_client.post(
            "/school/teachers",
            json=teacher.model_dump(),
        )


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(2)
def test_read_teachers_all():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/teachers",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert isinstance(body["data"], list)


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(3)
def test_read_teacher_by_param():

    from fastapi.testclient import TestClient
    from mainapp.main import app

    test_client = TestClient(app)

    teacher_body = {
        "firstname": "Richard",
        "lastname": "Roe",
    }

    teacher_firstname =  teacher_body["firstname"]
    teacher_lastname = teacher_body["lastname"]

    from urllib.parse import quote
    encoded_teacher_firstname = quote(teacher_firstname)
    encoded_teacher_lastname = quote(teacher_lastname)
    response = test_client.get(
        "/school/teachers",
        params={
            "firstname": encoded_teacher_firstname,
            "lastname": encoded_teacher_lastname,
        },
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["firstname"] == teacher_firstname
    assert body["data"]["lastname"] == teacher_lastname


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_teacher_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/teachers",
    )
    teacher_body = response.json()["data"][0]
    teacher_id = teacher_body["id"]


    response = test_client.get(
        f"/school/teachers/{teacher_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == teacher_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(5)
def test_put_teacher():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    teacher_body = {
        "firstname": "Richard",
        "lastname": "Roe",
    }

    teacher_firstname =  teacher_body["firstname"]
    teacher_lastname = teacher_body["lastname"]

    from urllib.parse import quote
    encoded_teacher_firstname = quote(teacher_firstname)
    encoded_teacher_lastname = quote(teacher_lastname)
    response = test_client.get(
        "/school/teachers",
        params={
            "firstname": encoded_teacher_firstname,
            "lastname": encoded_teacher_lastname,
        },
    )
    teacher_body = response.json()["data"]
    teacher_id = teacher_body["id"]


    new_firstname = "Richardey"
    new_lastname = "Roeny"

    response = test_client.put(
        f"/school/teachers/{teacher_id}",
        json={
            "firstname": new_firstname,
            "lastname": new_lastname,
            "description": "updated",
        }
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == teacher_id
    assert body["data"]["firstname"] == new_firstname
    assert body["data"]["lastname"] == new_lastname


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(6)
def test_delete_teacher():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    teacher_body = {
        "firstname": "Richardey",
        "lastname": "Roeny",
    }

    teacher_firstname =  teacher_body["firstname"]
    teacher_lastname = teacher_body["lastname"]

    from urllib.parse import quote
    encoded_teacher_firstname = quote(teacher_firstname)
    encoded_teacher_lastname = quote(teacher_lastname)
    response = test_client.get(
        "/school/teachers",
        params={
            "firstname": encoded_teacher_firstname,
            "lastname": encoded_teacher_lastname,
        },
    )
    teacher_body = response.json()["data"]
    teacher_id = teacher_body["id"]


    response = test_client.delete(
        f"/school/teachers/{teacher_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
