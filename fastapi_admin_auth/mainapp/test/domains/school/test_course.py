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
def test_create_course():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # 0: create a teacher and a student
    teacher_r = test_client.post(
        "/school/teachers",
        json={
            "firstname": "Dummy",
            "lastname": "Dum",
        },
    )
    teacher_id = teacher_r.json()["data"]["id"]
    student_r = test_client.post(
        "/school/students",
        json={
            "firstname": "Rummy",
            "lastname": "Rum",
        },
    )
    student_id = student_r.json()["data"]["id"]

    # Create by json: with certificate
    certificate_body = {
        "name": "test",
        "description": "test_desc",
    }
    course_body = {
        "name": "test",
        "description": "test_desc",
        "certificate": certificate_body,
        "teacher_id": teacher_id,
        "students": [student_id],
    }
    response = test_client.post(
        "/school/courses",
        json=course_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


    # Create by Model with foreign key
    from mainapp.domains.school.textbook.models import Textbook

    textbook = Textbook(name="textbook testA", description="textbook_testA")
    response = test_client.post(
        "/school/textbooks",
        json=textbook.model_dump(),
    )

    from urllib.parse import quote
    encoded_textbook_name = quote(textbook.name)

    textbook_r = test_client.get(
        "/school/textbooks",
        params={
            "name": encoded_textbook_name,
        },
    )
    textbook_model_id = textbook_r.json()["data"][0]["id"]

    certificate_body = {
        "name": "test2",
        "description": "test_desc2",
    }
    course_body = {
        "name": "test2",
        "description": "test_desc2",
        "certificate": certificate_body,
        "book_id": textbook_model_id,
        "teacher_id": teacher_id,
        "students": [student_id],
    }
    response = test_client.post(
        "/school/courses",
        json=course_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(2)
def test_read_courses_all():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/courses",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert isinstance(body["data"], list)


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(3)
def test_read_course_by_param():

    from fastapi.testclient import TestClient
    from mainapp.main import app

    test_client = TestClient(app)

    course_body = {
        "name": "test",
        "description": "test_desc",
    }
    course_name = course_body["name"]

    from urllib.parse import quote
    encoded_course_name = quote(course_name)

    response = test_client.get(
        "/school/courses",
        params={
            "name": encoded_course_name,
        },
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"][0]
    assert d["name"] == course_name

@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_course_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/courses",
    )
    course = response.json()["data"][0]
    course_id = course["id"]


    response = test_client.get(
        f"/school/courses/{course_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"]
    assert d["id"] == course_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(5)
def test_put_course():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    course_body = {
        "name": "test",
        "description": "test_desc",
    }
    course_name = course_body["name"]

    from urllib.parse import quote
    encoded_course_name = quote(course_name)

    response = test_client.get(
        "/school/courses",
        params={
            "name": encoded_course_name,
        },
    )
    course = response.json()["data"][0]
    course_id = course["id"]

    # MultiCourseWithStudentResponse
    course.pop("certificate")
    course["students"] = [s["id"] for s in course["students"]]

    # Update simple values
    new_name = "test-updated"
    new_desc = "updated"

    course["name"] = new_name
    course["description"] = new_desc

    response = test_client.put(
        f"/school/courses/{course_id}",
        json=course,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1

    d = body["data"]
    assert d["id"] == course_id
    assert d["name"] == new_name


    # # update One-to-One relations
    # course_body["certificate_id"] = new_name
    # course_body["description"] = "updated"

    # response = test_client.put(
    #     f"/school/courses/{course_id}",
    #     json=course_body,
    # )
    # response.raise_for_status()
    # body = response.json()
    # assert body["code"] == 1
    # assert body["data"]["id"] == course_id
    # assert body["data"]["name"] == new_name


# @pytest.mark.usefixtures("setup", "teardown")
# @pytest.mark.order(5)
# def test_put_course_certificate():

#     from fastapi.testclient import TestClient
#     from mainapp.main import app
    
#     test_client = TestClient(app)

#     response = test_client.get(
#         "/school/courses",
#     )
#     course = response.json()["data"][0]
#     course_id = course_body["id"]


#     new_name = "test-updated"
#     response = test_client.put(
#         f"/school/courses/{course_id}",
#         json={
#             "name": new_name,
#             "description": "updated",
#         }
#     )
#     response.raise_for_status()
#     body = response.json()
#     assert body["code"] == 1
#     assert body["data"]["id"] == course_id
#     assert body["data"]["name"] == new_name


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(6)
def test_delete_course():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    course_body = {
        "name": "test-updated",
        "description": "updated",
    }
    course_name = course_body["name"]

    from urllib.parse import quote
    encoded_course_name = quote(course_name)

    response = test_client.get(
        "/school/courses",
        params={
            "name": encoded_course_name,
        },
    )
    course = response.json()["data"][0]
    course_id = course["id"]


    response = test_client.delete(
        f"/school/courses/{course_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
