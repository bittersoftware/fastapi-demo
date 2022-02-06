import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models
# from alembic import command

DB_CREDENTIALS = f"postgresql://{settings.database_username}:{settings.database_password}"
DB_CONN = f"{settings.database_hostname}:{settings.database_port}"
DB_NAME = f"{settings.database_name}_test"
SQLALCHEMY_DATABASE_URL = f"{DB_CREDENTIALS}@{DB_CONN}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session_db():
    # using alembic
    # comand.upgrade("head")
    # command.downgrade("base")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session_db):
    def override_get_db():
        try:
            yield session_db
        finally:
            session_db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "user@example.com", "password": "password123"}
    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user.get("id")})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session_db):
    posts_data = [
        {
            "title": "first_title",
            "content": "first content",
            "owner_id": test_user.get("id")
        },
        {
            "title": "second_title",
            "content": "second content",
            "owner_id": test_user.get("id")
        },
        {
            "title": "third_title",
            "content": "third content",
            "owner_id": test_user.get("id")
        }
    ]

    posts = list(map(lambda posts: models.Post(**posts), posts_data))

    session_db.add_all(posts)
    session_db.commit()
    return session_db.query(models.Post).all()
