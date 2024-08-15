import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.base import Base
from fastapi.testclient import TestClient
from core.app import app
from core.dependencies import get_database_session
import tempfile

# Create a temporary file for the SQLite database
db_file = tempfile.NamedTemporaryFile(delete=False)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_file.name}"

# Create an engine and sessionmaker
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the dependency to use the testing session
def override_get_database_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database_session] = override_get_database_session

# Create a TestClient instance
client = TestClient(app)


# Pytest fixture to set up the database
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create the database schema
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests are done
    Base.metadata.drop_all(bind=engine)
    # Close and remove the temporary file
    db_file.close()


def test_create_user():
    response = client.post(
        "/users/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_login():
    response = client.post(
        "/users/token", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_book():
    # First, login to get the access token
    response = client.post(
        "/users/token", data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]

    # Now create a book
    response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book",
            "status": "read",
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"


def test_read_books():
    # First, login to get the access token
    response = client.post(
        "/users/token", data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    response = client.get(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_book():
    # First, login to get the access token
    response = client.post(
        "/users/token", data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]

    # Create a book to update
    response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book to Update",
            "status": "to_read",
        },
    )
    assert response.status_code == 200
    book_id = response.json()["id"]

    # Now update the book
    response = client.put(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Test Book",
            "status": "read",
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Book"
    assert response.json()["status"] == "read"


def test_delete_book():
    # First, login to get the access token
    response = client.post(
        "/users/token", data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]

    # Create a book to delete
    response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book to Delete",
            "status": "to_read",
        },
    )
    assert response.status_code == 200
    book_id = response.json()["id"]

    # Now delete the book
    response = client.delete(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == book_id

    # Verify the book was deleted
    response = client.get(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
