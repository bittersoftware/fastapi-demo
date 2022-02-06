import pytest
from jose import jwt
from app import schemas
from app.config import settings


def test_root(client):
    response = client.get("/")
    assert response.json().get("message") == "Hello World"
    assert response.status_code == 200


def test_creat_user(client, test_user):
    response = client.post(
        "/users/", json={"email": "joao5@email.com", "password": "pass123"})

    new_user = schemas.UserOutput(**response.json())
    assert new_user.email == "joao5@email.com"
    assert response.status_code == 201


def test_get_user(client, test_user):
    user_id = 1
    response = client.get(f"/users/{user_id}")
    assert response.json().get("email") == test_user.get("email")


def test_login_user(client, test_user):
    response = client.post(
        "/login", data={"username": test_user.get("email"), "password": test_user.get("password")})

    login_response = schemas.Token(**response.json())

    payload = jwt.decode(login_response.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])

    id: str = payload.get("user_id")

    assert id == test_user.get("id")
    assert login_response.token_type == "bearer"
    assert response.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ("wrong.email@email.com", "password123", 403),
    ("joao5@email.com", "wrong.password", 403),
    ("wrong.email@email.com", "wrong.password", 403),
    (None, "password123", 422),
    ("joao5@email.com", None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    response = client.post(
        "/login", data={"username": email, "password": password})

    assert response.status_code == status_code
    # assert response.json().get("detail") == "Invalid Credentials"
