import pytest
from flask import Flask
from flask.testing import FlaskClient

from api import create_app, db


@pytest.fixture()
def app() -> Flask: # type: ignore
    app = create_app(SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient: # type: ignore
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()

        db.drop_all()
        db.create_all()
        # register()

        yield client
        db.drop_all()
        app_ctx.pop()
