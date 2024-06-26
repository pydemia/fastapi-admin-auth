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
def test_create_student():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # Create by json
    student_body = {
        "firstname": "John",
        "lastname": "Doe",
    }
    response = test_client.post(
        "/school/students",
        json=student_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


    # Create by Model
    from mainapp.domains.school.student.models import Student

    student_0 = Student(firstname="Andrew", lastname="Evans", description="student 0")
    student_1 = Student(firstname="Joseph", lastname="Davis", description="student 1")
    student_2 = Student(firstname="Christopher", lastname="Robinson", description="student 2")
    student_3 = Student(firstname="Sofia", lastname="Thompson", description="student 3")

    students = [
        student_0, student_1, student_2, student_3,
    ]
    for student in students:
        response = test_client.post(
            "/school/students",
            json=student.model_dump(),
        )


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(2)
def test_read_students_all():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/students",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert isinstance(body["data"], list)


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(3)
def test_read_student_by_param():

    from fastapi.testclient import TestClient
    from mainapp.main import app

    test_client = TestClient(app)

    student_body = {
        "firstname": "John",
        "lastname": "Doe",
    }
    student_firstname =  student_body["firstname"]
    student_lastname = student_body["lastname"]

    from urllib.parse import quote
    encoded_student_firstname = quote(student_firstname)
    encoded_student_lastname = quote(student_lastname)
    response = test_client.get(
        "/school/students",
        params={
            "firstname": encoded_student_firstname,
            "lastname": encoded_student_lastname,
        },
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"][0]
    assert d["firstname"] == student_firstname
    assert d["lastname"] == student_lastname


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_student_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/students",
    )
    student = response.json()["data"][0]
    student_id = student["id"]


    response = test_client.get(
        f"/school/students/{student_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"]
    assert d["id"] == student_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(5)
def test_put_student():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    student_body = {
        "firstname": "John",
        "lastname": "Doe",
    }
    student_firstname =  student_body["firstname"]
    student_lastname = student_body["lastname"]

    from urllib.parse import quote
    encoded_student_firstname = quote(student_firstname)
    encoded_student_lastname = quote(student_lastname)
    response = test_client.get(
        "/school/students",
        params={
            "firstname": encoded_student_firstname,
            "lastname": encoded_student_lastname,
        },
    )
    student = response.json()["data"][0]
    student_id = student["id"]


    new_firstname = "Johney"
    new_lastname = "Doeny"

    response = test_client.put(
        f"/school/students/{student_id}",
        json={
            "firstname": new_firstname,
            "lastname": new_lastname,
            "description": "updated",
        }
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"]
    assert d["id"] == student_id
    assert d["firstname"] == new_firstname
    assert d["lastname"] == new_lastname


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(6)
def test_delete_student():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    student_body = {
        "firstname": "Johney",
        "lastname": "Doeny",
    }
    student_firstname =  student_body["firstname"]
    student_lastname = student_body["lastname"]

    from urllib.parse import quote
    encoded_student_firstname = quote(student_firstname)
    encoded_student_lastname = quote(student_lastname)
    response = test_client.get(
        "/school/students",
        params={
            "firstname": encoded_student_firstname,
            "lastname": encoded_student_lastname,
        },
    )
    student = response.json()["data"][0]
    student_id = student["id"]


    response = test_client.delete(
        f"/school/students/{student_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
