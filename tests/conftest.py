import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from microblog.app import app
from microblog.cli import create_user
from microblog.db import engine

os.environ["MICROBLOG_DB__uri"] = "postgresql://postgres:postgres@db:5432/microblog_test"


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Clean database between tests"""
    with Session(engine) as session:
        # Delete all data from tables
        session.execute(text('DELETE FROM "like"'))
        session.execute(text('DELETE FROM "post"'))
        session.execute(text('DELETE FROM "social"'))
        session.execute(text('DELETE FROM "user"'))
        session.commit()
    yield


@pytest.fixture(scope="function")
def api_client():
    return TestClient(app)


def create_api_client_authenticated(username):
    try:
        create_user(f"{username}@microblog.com", username, username)
    except IntegrityError:
        pass

    client = TestClient(app)
    token = client.post(
        "/token",
        data={"username": username, "password": username},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="function")
def api_client_user1():
    return create_api_client_authenticated("user1")


@pytest.fixture(scope="function")
def api_client_user2():
    return create_api_client_authenticated("user2")