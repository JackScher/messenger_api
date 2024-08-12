from flask.testing import FlaskClient
from api.models import User, Post


def test_read(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    r = client.get("/api/post", data={"post_uuid": p.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.get("/api/post", data={"post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.get("/api/post", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    test_uuid = p.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.get("/api/post", json={"post_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404 

    p.delete()
    r = client.get("/api/post", json={"post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    p.restore()

    r = client.get("/api/post", json={"post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "test post body..."
    assert r.json["message"] == "Get post successful"


def test_read_all(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    u1: User = User(username="test_username_1", email="test_email1@gmail.com", password="test_password_1")
    u1.save()

    p1: Post = Post(body="test post 1 body...", title="test_title 1", description="test_description 1", user_id=u.id, user=u)
    p1.save()

    p2: Post = Post(body="test post 2 body...", title="test_title 2", description="test_description 2", user_id=u.id, user=u)
    p2.save()

    p3: Post = Post(body="test post 3 body...", title="test_title 3", description="test_description 3", user_id=u.id, user=u)
    p3.save()
    p3.delete()

    p4: Post = Post(body="test post 4 body...", title="test_title 4", description="test_description 3", user_id=u1.id, user=u1)
    p4.save()

    r = client.get("/api/post/get_all", data={"user_uuid": u.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.get("/api/post/get_all", data={"user_uuid": u.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.get("/api/post/get_all", json={"user_uuid": 111}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    test_uuid = u.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.get("/api/post/get_all", json={"user_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    u.delete()
    r = client.get("/api/post/get_all", json={"user_uuid": u.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    r = client.get("/api/post/get_all", json={"user_uuid": u.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert len(r.json["data"].keys()) == 2
    assert r.json["data"]["0"]["body"] == "test post 1 body..."
    assert r.json["data"]["1"]["body"] == "test post 2 body..."
    assert r.json["message"] == "Get all posts successful"

    r = client.get("/api/post/get_all", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert len(r.json["data"].keys()) == 3
    assert r.json["data"]["0"]["body"] == "test post 1 body..."
    assert r.json["data"]["1"]["body"] == "test post 2 body..."
    assert r.json["data"]["2"]["body"] == "test post 4 body..."
    assert r.json["message"] == "Get all posts successful"


def test_create(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    r = client.post("/api/post/create", data={"user_uuid": u.uuid, "body": "test post body...", "title": "test_title", "description": "test_description"})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.post("/api/post/create", data={"user_uuid": u.uuid, "body": "test post body...", "title": "test_title", "description": "test_description"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.post("/api/post/create", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.post("/api/post/create", json={"user_uuid": u.uuid, "body": "test post body...", "title": "test_title", "description": "test_description"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    r = client.post("/api/post/create", json={"user_uuid": u.uuid, "body": "test post body...", "title": "test_title", "description": "test_description"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "test post body..."
    assert r.json["message"] == "Post created"


def test_update(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    p: Post = Post(body="test post body...", user_id=u.id, user=u, title="test_title", description="test_description")
    p.save()

    r = client.patch("/api/post/update", data={"user_uuid": u.uuid, "post_uuid": p.uuid, "body": "new post body..."})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.patch("/api/post/update", data={"user_uuid": u.uuid, "post_uuid": p.uuid, "body": "new post body..."}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.patch("/api/post/update", json={"user_uuid": u.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.patch("/api/post/update", json={"user_uuid": u.uuid, "post_uuid": p.uuid, "body": "new post body...", "title": "new_test_title", "description": "new_test_description"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    p.delete()
    r = client.patch("/api/post/update", json={"user_uuid": u.uuid, "post_uuid": p.uuid, "body": "new post body...", "title": "new_test_title", "description": "new_test_description"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    p.restore()

    r = client.patch("/api/post/update", json={"user_uuid": u.uuid, "post_uuid": p.uuid, "body": "new post body...", "title": "new_test_title", "description": "new_test_description"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "new post body..."
    assert p.body == "new post body..."
    assert p.title == "new_test_title"
    assert p.description == "new_test_description"
    assert r.json["message"] == "Post updated"


def test_delete(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    r = client.delete("/api/post/delete", data={"user_uuid": u.uuid, "post_uuid": p.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.delete("/api/post/delete", data={"user_uuid": u.uuid, "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.delete("/api/post/delete", json={"user_uuid": u.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.delete("/api/post/delete", json={"user_uuid": u.uuid, "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    test_uuid = p.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.delete("/api/post/delete", json={"user_uuid": u.uuid, "post_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404   

    p.delete()
    r = client.delete("/api/post/delete", json={"user_uuid": u.uuid, "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    p.restore()

    r = client.delete("/api/post/delete", json={"user_uuid": u.uuid, "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "test post body..."
    assert r.json["message"] == "Post deleted"


def test_restore(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()
    p.delete()

    r = client.post("/api/post/restore", data={"user_uuid": u.uuid, "post_uuid": p.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.post("/api/post/restore", data={"user_uuid": u.uuid, "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.post("/api/post/restore", json={"user_uuid": u.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.post("/api/post/restore", json={"user_uuid": u.uuid, "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    test_uuid = p.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.post("/api/post/restore", json={"user_uuid": u.uuid, "post_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    p.restore()
    r = client.post("/api/post/restore", json={"user_uuid": u.uuid, "post_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    p.delete()

    r = client.post("/api/post/restore", json={"user_uuid": u.uuid, "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "test post body..."
    assert r.json["message"] == "Post restored"
