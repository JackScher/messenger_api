from flask.testing import FlaskClient
from api.models import User


def test_login(client: FlaskClient) -> None:
    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    r = client.post("/auth/login", data={"email": "test_email@gmail.com", "password": "test_password"})
    assert r
    assert r.status_code == 415

    r = client.post("/auth/login", json={"email": "test_email@gmail.com"})
    assert r
    assert r.status_code == 422

    r = client.post("/auth/login", json={"email": "WRONG_EMAIL@gmail.com", "password": "test_password"})
    assert r
    assert r.status_code == 404

    r = client.post("/auth/login", json={"email": "test_email@gmail.com", "password": "WRONG_PASSWORD"})
    assert r
    assert r.status_code == 404

    r = client.post("/auth/login", json={"email": "test_email@gmail.com", "password": "test_password"})
    assert r
    assert r.status_code == 200
    assert 'access_token' in r.json["data"]
    assert r.json["message"] == "Login user successful"


def test_register(client: FlaskClient) -> None:
    r = client.post("/auth/register", data={"email": "test_email@gmail.com", "password": "test_password", "first_name": "test_first_name", "last_name": "test_last_name"})
    assert r
    assert r.status_code == 415

    r = client.post("/auth/register", json={"email": "test_email@gmail.com"})
    assert r
    assert r.status_code == 422

    u: User = User(username="test_username", email="test_email@gmail.com", password="test_password")
    u.save()

    r = client.post("/auth/register", json={"username": "test_username", "email": "test_email_1@gmail.com", "password": "test_password", "first_name": "test_first_name", "last_name": "test_last_name"})
    assert r
    assert r.status_code == 422

    r = client.post("/auth/register", json={"username": "test_username_1", "email": "test_email@gmail.com", "password": "test_password", "first_name": "test_first_name", "last_name": "test_last_name"})
    assert r
    assert r.status_code == 422

    r = client.post("/auth/register", json={"username": "test_username_1", "email": "test_email_1@gmail.com", "password": "test_password1", "first_name": "test_first_name", "last_name": "test_last_name"})
    assert r
    assert r.status_code == 200
