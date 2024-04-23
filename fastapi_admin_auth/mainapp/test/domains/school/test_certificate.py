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
def test_create_certificate():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    # Create by json
    certificate_body = {
        "name": "test",
        "description": "test_desc",
    }
    response = test_client.post(
        "/school/certificates",
        json=certificate_body,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1


    # Create by Model
    from mainapp.domains.school.certificate.models import Certificate

    certificate_0 = Certificate(name="certificate 0", description="certificate_0")
    certificate_1 = Certificate(name="certificate 1", description="certificate_1")
    certificate_2 = Certificate(name="certificate 2", description="certificate_2")
    certificate_3 = Certificate(name="certificate 3", description="certificate_3")


    certificates = [
        certificate_0, certificate_1, certificate_2, certificate_3,
    ]
    for certificate in certificates:
        response = test_client.post(
            "/school/certificates",
            json=certificate.model_dump(),
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


    certificate_a = Certificate(name="certificate a", description="certificate_a", book_id=textbook_a_model.id)
    certificate_b = Certificate(name="certificate b", description="certificate_b", book_id=textbook_b_model.id)

    certificates = [
        certificate_a, certificate_b,
    ]
    for certificate in certificates:
        response = test_client.post(
            "/school/certificates",
            json=certificate.model_dump(),
        )



@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(2)
def test_read_certificates_all():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/certificates",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert isinstance(body["data"], list)


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(3)
def test_read_certificate_by_param():

    from fastapi.testclient import TestClient
    from mainapp.main import app

    test_client = TestClient(app)


    certificate_body = {
        "name": "test",
        "description": "test_desc",
    }
    certificate_name = certificate_body["name"]

    from urllib.parse import quote
    encoded_certificate_name = quote(certificate_name)

    response = test_client.get(
        "/school/certificates",
        params={
            "name": encoded_certificate_name,
        },
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"][0]["name"] == certificate_name

@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(4)
def test_read_certificate_by_id():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/certificates",
    )
    certificate_body = response.json()["data"][0]
    certificate_id = certificate_body["id"]


    response = test_client.get(
        f"/school/certificates/{certificate_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == certificate_id


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(5)
def test_put_certificate():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/certificates",
    )
    certificate_body = response.json()["data"][0]
    certificate_id = certificate_body["id"]


    new_name = "test-updated"
    response = test_client.put(
        f"/school/certificates/{certificate_id}",
        json={
            "name": new_name,
            "description": "updated",
        }
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
    assert body["data"]["id"] == certificate_id
    assert body["data"]["name"] == new_name


@pytest.mark.usefixtures("setup", "teardown")
@pytest.mark.order(6)
def test_delete_certificate():

    from fastapi.testclient import TestClient
    from mainapp.main import app
    
    test_client = TestClient(app)

    response = test_client.get(
        "/school/certificates",
    )
    certificate_body = response.json()["data"][0]
    certificate_id = certificate_body["id"]


    response = test_client.delete(
        f"/school/certificates/{certificate_id}",
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 1
