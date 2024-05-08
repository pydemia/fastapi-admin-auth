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

    # Create by json
    certificate_body = {
        "name": "test",
        "description": "test_desc",
    }
    course_body = {
        "name": "test",
        "description": "test_desc",
        "certificate": certificate_body,
    }
    response = test_client.post(
        "/school/courses",
        json=course_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


    # Create by Model
    # from mainapp.domains.school.course.models import Course, Certificate
    from mainapp.domains.school.course.schema import CreateCourseRequest, CertificateRequest

    course_0 = CreateCourseRequest(
        name="course 0", description="course_0",
        certificate=CertificateRequest(name="cert 0", description="cert_0")
    )
    course_1 = CreateCourseRequest(
        name="course 1", description="course_1",
        certificate=CertificateRequest(name="cert 1", description="cert_1")
    )
    course_2 = CreateCourseRequest(
        name="course 2", description="course_2",
        certificate=CertificateRequest(name="cert 2", description="cert_2")
    )
    course_3 = CreateCourseRequest(
        name="course 3", description="course_3",
        certificate=CertificateRequest(name="cert 3", description="cert_3")
    )


    courses = [
        course_0, course_1, course_2, course_3,
    ]
    for course in courses:
        response = test_client.post(
            "/school/courses",
            json=course.model_dump(),
        )


    # Create by Model with foreign key
    from mainapp.domains.school.textbook.models import Textbook

    textbook_a = Textbook(name="textbook a", description="textbook_a")
    textbook_b = Textbook(name="textbook b", description="textbook_b")

    textbooks = [
        textbook_a, textbook_b,
    ]
    for textbook in textbooks:
        response = test_client.post(
            "/school/textbooks",
            json=textbook.model_dump(),
        )

    from urllib.parse import quote
    encoded_textbook_a_name = quote(textbook_a.name)
    encoded_textbook_b_name = quote(textbook_b.name)

    textbook_a_response = test_client.get(
        "/school/textbooks",
        params={
            "name": encoded_textbook_a_name,
        },
    )
    textbook_a_model = Textbook.model_validate(textbook_a_response.json()["data"])

    textbook_b_response = test_client.get(
        "/school/textbooks",
        params={
            "name": encoded_textbook_b_name,
        },
    )
    textbook_b_model = Textbook.model_validate(textbook_b_response.json()["data"])


    course_a = CreateCourseRequest(
        name="course a", description="course_a",
        book_id=textbook_a_model.id,
        certificate=CertificateRequest(name="cert a", description="cert_a"),
    )
    course_b = CreateCourseRequest(
        name="course b", description="course_b",
        book_id=textbook_b_model.id,
        certificate=CertificateRequest(name="cert a", description="cert_a"),
    )

    courses = [
        course_a, course_b,
    ]
    for course in courses:
        response = test_client.post(
            "/school/courses",
            json=course.model_dump(),
        )



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
    assert body["data"][0]["name"] == course_name

@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_course_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/courses",
    )
    course_body = response.json()["data"][0]
    course_id = course_body["id"]


    response = test_client.get(
        f"/school/courses/{course_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == course_id


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
    course_body = response.json()["data"]
    course_id = course_body["id"]

    # Update simple values
    new_name = "test-updated"
    new_desc = "updated"

    course_body["name"] = new_name
    course_body["description"] = new_desc

    response = test_client.put(
        f"/school/courses/{course_id}",
        json=course_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == course_id
    assert body["data"]["name"] == new_name


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
#     course_body = response.json()["data"][0]
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
    course_body = response.json()["data"]
    course_id = course_body["id"]


    response = test_client.delete(
        f"/school/courses/{course_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
