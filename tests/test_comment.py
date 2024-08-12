from datetime import datetime, timedelta
from flask.testing import FlaskClient
from api.models import User, Post, Comment


def test_read(client: FlaskClient) -> None:
    u: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    c: Comment = Comment(body="test comment body 1", post_id=p.id, post=p, user_id=u.id, user=u)
    c.save()

    r = client.get("/api/comment", data={"comment_uuid": c.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.get("/api/comment", data={"comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.get("/api/comment", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    test_uuid = c.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.get("/api/comment", json={"comment_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    c.delete()
    r = client.get("/api/comment", json={"comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    c.restore()

    r = client.get("/api/comment", json={"comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "test comment body 1"
    assert r.json["message"] == "Get comment successful"


def test_read_all(client: FlaskClient) -> None:
    u1: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u1.save()

    u2: User = User(username="test_username2", email="test_email2@gmail.com", password="test_password2", first_name="test_first_name2", last_name="test_last_name2")
    u2.save()

    p1: Post = Post(body="test post body1...", title="test_title1", description="test_description1", user_id=u1.id, user=u1)
    p1.save()

    c1: Comment = Comment(body="test comment body 1", post_id=p1.id, post=p1, user_id=u2.id, user=u2)
    c1.save()

    c2: Comment = Comment(body="test comment body 2", post_id=p1.id, post=p1, user_id=u2.id, user=u2)
    c2.save()

    c3: Comment = Comment(body="test comment body 3", post_id=p1.id, post=p1, user_id=u1.id, user=u1)
    c3.save()

    c4: Comment = Comment(body="test comment body 4", user_id=u1.id, user=u1, parent_id=c1.id, parent_comment=c1)
    c4.save()

    r = client.get("/api/comment/get_all", data={})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u1.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.get("/api/comment/get_all", data={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.get("/api/comment/get_all", json={"user_uuid": 1}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    test_uuid = u1.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.get("/api/comment/get_all", json={"user_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    u1.delete()
    r = client.get("/api/comment", json={"comment_uuid": u1.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u1.restore()

    test_uuid = p1.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.get("/api/comment/get_all", json={"post_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    p1.delete()
    r = client.get("/api/comment/get_all", json={"post_uuid": p1.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    p1.restore()

    test_uuid = c1.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.get("/api/comment/get_all", json={"comment_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    c1.delete()
    r = client.get("/api/comment/get_all", json={"comment_uuid": c1.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    c1.restore()

    r = client.get("/api/comment/get_all", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert len(r.json["data"].keys()) == 4
    assert r.json["message"] == "Get all comments successful"

    r = client.get("/api/comment/get_all", json={"user_uuid": u2.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert len(r.json["data"].keys()) == 2
    assert r.json["message"] == "Get all comments successful"

    r = client.get("/api/comment/get_all", json={"post_uuid": p1.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert len(r.json["data"].keys()) == 3
    assert r.json["message"] == "Get all comments successful"

    r = client.get("/api/comment/get_all", json={"comment_uuid": c1.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert len(r.json["data"].keys()) == 1
    assert r.json["message"] == "Get all comments successful"


def test_create(client: FlaskClient) -> None:
    u: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    c: Comment = Comment(body="test comment body 1", post_id=p.id, post=p, user_id=u.id, user=u)
    c.save()

    r = client.post("/api/comment/create", data={"user_uuid": u.uuid, "body": "test comment body 2"})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.post("/api/comment/create", data={"user_uuid": u.uuid, "body": "test comment body 2"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.post("/api/comment/create", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.post("/api/comment/create", json={"user_uuid": u.uuid, "body": "test comment body 2", "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    test_uuid = p.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.post("/api/comment/create", json={"user_uuid": u.uuid, "body": "test comment body 2", "post_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    p.delete()
    r = client.post("/api/comment/create", json={"user_uuid": u.uuid, "body": "test comment body 2", "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    p.restore()

    r = client.post("/api/comment/create", json={"user_uuid": u.uuid, "body": "test comment body 2", "parent_uuid": "wrong_uuid"}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    assert r.json["message"] == "Parent comment doesn`t exist"

    assert len(c.answers) == 0
    r = client.post("/api/comment/create", json={"user_uuid": u.uuid, "body": "test comment body 2", "parent_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "test comment body 2"
    assert r.json["message"] == "Comment created"
    assert len(c.answers) == 1

    assert len(p.comments) == 1
    r = client.post("/api/comment/create", json={"user_uuid": u.uuid, "body": "test comment body 3", "post_uuid": p.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "test comment body 3"
    assert r.json["message"] == "Comment created"
    assert len(p.comments) == 2


def test_update(client: FlaskClient) -> None:
    u: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    c: Comment = Comment(body="test comment body 1", post_id=p.id, post=p, user_id=u.id, user=u)
    c.save()

    r = client.patch("/api/comment/update", data={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": c.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.patch("/api/comment/update", data={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.patch("/api/comment/update", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.patch("/api/comment/update", json={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    c.delete()
    r = client.patch("/api/comment/update", json={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    c.restore()

    test_uuid = c.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.patch("/api/comment/update", json={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    r = client.patch("/api/comment/update", json={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["data"]["body"] == "new test comment body 1"
    assert r.json["message"] == "Comment updated"


def test_delete(client: FlaskClient) -> None:
    u: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    c: Comment = Comment(body="test comment body 1", post_id=p.id, post=p, user_id=u.id, user=u)
    c.save()

    r = client.delete("/api/comment/delete", data={"user_uuid": u.uuid, "comment_uuid": c.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.delete("/api/comment/delete", data={"user_uuid": u.uuid, "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.delete("/api/comment/delete", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.delete("/api/comment/delete", json={"user_uuid": u.uuid, "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    c.delete()
    r = client.delete("/api/comment/delete", json={"user_uuid": u.uuid, "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    c.restore()

    test_uuid = c.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.delete("/api/comment/delete", json={"user_uuid": u.uuid, "comment_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    r = client.delete("/api/comment/delete", json={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["message"] == "Comment deleted"
    assert r.json["data"]["body"] == "test comment body 1"
    assert p.comments[0].is_deleted == True


def test_restore(client: FlaskClient) -> None:
    u: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    c: Comment = Comment(body="test comment body 1", post_id=p.id, post=p, user_id=u.id, user=u)
    c.save()
    c.delete()

    r = client.post("/api/comment/restore", data={"user_uuid": u.uuid, "comment_uuid": c.uuid})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.post("/api/comment/restore", data={"user_uuid": u.uuid, "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.post("/api/comment/restore", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.post("/api/comment/restore", json={"user_uuid": u.uuid, "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    c.restore()
    r = client.post("/api/comment/restore", json={"user_uuid": u.uuid, "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    c.delete()

    test_uuid = c.uuid
    test_uuid = test_uuid[0:-4] + "test"
    r = client.post("/api/comment/restore", json={"user_uuid": u.uuid, "comment_uuid": test_uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404

    r = client.post("/api/comment/restore", json={"user_uuid": u.uuid, "body": "new test comment body 1", "comment_uuid": c.uuid}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["message"] == "Comment restored"
    assert r.json["data"]["body"] == "test comment body 1"
    assert p.comments[0].is_deleted == False


def test_comments_daily_breakdown(client: FlaskClient) -> None:
    u: User = User(username="test_username1", email="test_email1@gmail.com", password="test_password", first_name="test_first_name", last_name="test_last_name")
    u.save()

    p: Post = Post(body="test post body...", title="test_title", description="test_description", user_id=u.id, user=u)
    p.save()

    c0: Comment = Comment(body="test comment body ", post_id=p.id, post=p, user_id=u.id, user=u)
    c0.save()

    c1: Comment = Comment(body="test comment body 1", post_id=p.id, post=p, user_id=u.id, user=u)
    c1.created_at = datetime.now() - timedelta(days=5)
    c1.save()

    c2: Comment = Comment(body="test comment body 2", post_id=p.id, post=p, user_id=u.id, user=u)
    c2.created_at = datetime.now() - timedelta(days=4)
    c2.save()

    c3: Comment = Comment(body="test comment body 3", post_id=p.id, post=p, user_id=u.id, user=u)
    c3.created_at = datetime.now() - timedelta(days=3)
    c3.save()

    c4: Comment = Comment(body="test comment body 4", post_id=p.id, post=p, user_id=u.id, user=u)
    c4.created_at = datetime.now() - timedelta(days=2)
    c4.save()

    date_from = datetime.now() - timedelta(days=6)
    date_to = datetime.now() - timedelta(days=2)
    date_from = date_from.strftime("%Y-%m-%d")
    date_to = date_to.strftime("%Y-%m-%d")

    r = client.get("/api/comment/comments_daily_breakdown", data={"date_from": date_from, "date_to": date_to})
    assert r
    assert r.status_code == 401

    r = client.post("/auth/login", json={"email": u.email, "password": "test_password"})
    access_token = r.json["data"]["access_token"]

    r = client.get("/api/comment/comments_daily_breakdown", data={"date_from": date_from, "date_to": date_to}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 415

    r = client.get("/api/comment/comments_daily_breakdown", json={}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 422

    u.delete()
    r = client.get("/api/comment/comments_daily_breakdown", json={"date_from": date_from, "date_to": date_to}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 404
    u.restore()

    r = client.get("/api/comment/comments_daily_breakdown", json={"date_from": date_from, "date_to": date_to}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["message"] == "Get comments daily breakdown successful"
    assert r.json["data"]["created"] == 3
    assert r.json["data"]["blocked"] == 0

    c1.is_blocked = True
    c1.save()

    r = client.get("/api/comment/comments_daily_breakdown", json={"date_from": date_from, "date_to": date_to}, headers={'Authorization': f'Bearer {access_token}'})
    assert r
    assert r.status_code == 200
    assert r.json["message"] == "Get comments daily breakdown successful"
    assert r.json["data"]["created"] == 2
    assert r.json["data"]["blocked"] == 1
