from re import I
import pytest
from app import models

LIKED_POST = 3


@pytest.fixture
def test_like(test_posts, session_db, test_user):
    new_like = models.Like(
        post_id=test_posts[LIKED_POST].id, user_id=test_user["id"])
    session_db.add(new_like)
    session_db.commit()


def test_like_post(authorized_client, test_posts, test_like):
    res = authorized_client.post(
        "/like/", json={"post_id": test_posts[LIKED_POST].id, "direction": 1})
    assert res.status_code == 409


def test_delete_like(authorized_client, test_posts, test_like):
    res = authorized_client.post(
        "/like/", json={"post_id": test_posts[LIKED_POST].id, "direction": 0})
    assert res.status_code == 201


def test_delete_like_non_exist(authorized_client, test_posts):
    res = authorized_client.post(
        "/like/", json={"post_id": test_posts[LIKED_POST].id, "direction": 0})
    assert res.status_code == 404


def test_like_post_non_exist(authorized_client):
    res = authorized_client.post(
        "/like/", json={"post_id": 99999, "direction": 0})
    assert res.status_code == 404


def test_like_unauthorized_user(client, test_posts):
    res = client.post(
        "/like/", json={"post_id": test_posts[LIKED_POST].id, "direction": 0})
    assert res.status_code == 401
