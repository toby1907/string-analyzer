
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_string(test_db):
    response = client.post(
        "/strings",
        json={"value": "hello world"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "hello world"
    assert data["properties"]["length"] == 11
    assert data["properties"]["word_count"] == 2
    assert data["properties"]["is_palindrome"] == False

def test_get_string(test_db):
    # First create a string
    client.post("/strings", json={"value": "test string"})
    
    # Then retrieve it
    response = client.get("/strings/test string")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "test string"

def test_natural_language_query(test_db):
    # Create some test data
    client.post("/strings", json={"value": "madam"})
    client.post("/strings", json={"value": "hello world"})
    
    response = client.get("/strings/filter-by-natural-language?query=palindromic strings")
    assert response.status_code == 200
    data = response.json()
    assert "interpreted_query" in data