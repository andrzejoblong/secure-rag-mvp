import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "RAG MVP API running"

def test_upload_document():
    # This is a placeholder, should use a real file in integration
    response = client.post("/documents", files={"file": ("test.txt", b"test content")})
    assert response.status_code == 200
    assert "id" in response.json()

def test_query():
    # Placeholder, should use real data after ingest
    response = client.post("/query", json={"question": "test", "top_k": 2})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
