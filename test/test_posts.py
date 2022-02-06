import pytest
from app import schemas


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    sorted_posts = sorted(res.json(), key=lambda v: v["Post"]["id"])
    for index, post in enumerate(sorted_posts):
        post = schemas.PostOutput(**post)
        assert post.Post.title == test_posts[index].title
        assert post.Post.content == test_posts[index].content
        assert post.Post.id == test_posts[index].id
        assert post.Post.created_at == test_posts[index].created_at
        assert post.Post.owner_id == test_posts[index].owner.id
        assert type(post.Post.owner) is schemas.UserOutput
    assert res.status_code == 200


def test_unauthorized_get_all_posts(client):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_get_one_posts(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_get_one_post_not_exist(authorized_client):
    res = authorized_client.get("/posts/88888")
    assert res.status_code == 404


def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOutput(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content
    assert res.status_code == 200


@pytest.mark.parametrize("title, content, published", [
    ("new title", "new content", True),
    ("second title", "second content", True),
    ("third title", "third content", False),

])
def test_create_post(authorized_client, test_user, title, content, published):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published})

    created_post = schemas.PostResponse(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user.get("id")


def test_create_post_published_default(authorized_client, test_user):
    res = authorized_client.post(
        "/posts/", json={"title": "test_title", "content": "content"})

    created_post = schemas.PostResponse(**res.json())
    assert res.status_code == 201
    assert created_post.title == "test_title"
    assert created_post.content == "content"
    assert created_post.published is True
    assert created_post.owner_id == test_user.get("id")


def test_unauthorized_create_post(client):
    res = client.post(
        "/posts/", json={"title": "test_title", "content": "content"})
    assert res.status_code == 401


def test_unauthorized_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_delete_post_success(authorized_client, test_posts):
    posts_before = len(authorized_client.get("/posts/").json())
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    posts_later = len(authorized_client.get("/posts/").json())
    assert res.status_code == 204
    assert posts_before - posts_later == 1


def test_delet_post_non_exist(authorized_client, test_posts):
    res = authorized_client.delete("/posts/800000")
    assert res.status_code == 404
