import pytest
import mongomock
from unittest.mock import patch
from bson.objectid import ObjectId

import app as app_module
from db import COLLECTION_NAME


@pytest.fixture(autouse=True)
def setup_db():
    # Use mongomock for testing instead of a real MongoDB instance
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.notesdb
    
    # Patch get_database so app.py calls our mock db
    with patch('app.get_database', return_value=mock_db):
        yield mock_db


@pytest.fixture
def client():
    app_module.app.testing = True
    with app_module.app.test_client() as client:
        yield client


def test_create_note(client):
    res = client.post("/notes", json={"title": "First", "content": "hello"})
    assert res.status_code == 201
    data = res.get_json()
    assert "id" in data
    assert data["title"] == "First"
    assert data["content"] == "hello"


def test_get_notes(client):
    client.post("/notes", json={"title": "x"})
    res = client.get("/notes")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_note(client):
    post_res = client.post("/notes", json={"title": "a", "content": "b"})
    note_id = post_res.get_json()["id"]
    
    res = client.get(f"/notes/{note_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == note_id


def test_update_note(client):
    post_res = client.post("/notes", json={"title": "a"})
    note_id = post_res.get_json()["id"]
    
    res = client.put(f"/notes/{note_id}", json={"title": "updated", "done": True})
    assert res.status_code == 200
    data = res.get_json()
    assert data["title"] == "updated"
    assert data["done"] is True


def test_delete_note(client):
    post_res = client.post("/notes", json={"title": "a"})
    note_id = post_res.get_json()["id"]
    
    res = client.delete(f"/notes/{note_id}")
    assert res.status_code == 204
    
    res2 = client.get(f"/notes/{note_id}")
    assert res2.status_code == 404


def test_create_without_title(client):
    res = client.post("/notes", json={"content": "no title"})
    assert res.status_code == 400


def test_get_nonexistent_note(client):
    """Verify 404 for missing resources"""
    fake_id = str(ObjectId())
    res = client.get(f"/notes/{fake_id}")
    assert res.status_code == 404

def test_update_nonexistent_note(client):
    """Verify 404 when updating missing resources"""
    fake_id = str(ObjectId())
    res = client.put(f"/notes/{fake_id}", json={"title": "Ghost"})
    assert res.status_code == 404

def test_delete_nonexistent_note(client):
    """Verify 404 when deleting missing resources"""
    fake_id = str(ObjectId())
    res = client.delete(f"/notes/{fake_id}")
    assert res.status_code == 404

def test_invalid_id_format(client):
    """Verify 400 when invalid string ID is used"""
    res = client.get("/notes/invalid-id")
    assert res.status_code == 400

def test_malformed_json_post(client):
    """Verify 400 for bad payloads"""
    res = client.post("/notes", data="not json", content_type='application/json')
    assert res.status_code == 400