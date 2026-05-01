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

def test_index_health_check(client):
    """Verify the root health endpoint works."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert "Notes & Todo API" in data["message"]

def test_partial_update_note(client):
    """Verify that updating one field doesn't overwrite others."""
    # Create note
    post_res = client.post("/notes", json={"title": "Old Title", "content": "Keep this", "done": False})
    note_id = post_res.get_json()["id"]
    
    # Update only 'done' to True
    res = client.put(f"/notes/{note_id}", json={"done": True})
    assert res.status_code == 200
    
    # Check that other fields are untouched
    data = res.get_json()
    assert data["done"] is True
    assert data["title"] == "Old Title"
    assert data["content"] == "Keep this"

def test_create_note_full_fields(client):
    """Verify all fields correctly insert."""
    res = client.post("/notes", json={"title": "All Fields", "content": "Testing 123", "done": True})
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "All Fields"
    assert data["content"] == "Testing 123"
    assert data["done"] is True

def test_create_note_with_tags(client):
    """Verify creating a note with tags."""
    res = client.post("/notes", json={"title": "Grocery", "tags": ["shopping", "urgent"]})
    assert res.status_code == 201
    data = res.get_json()
    assert "shopping" in data["tags"]

def test_filter_notes_by_tag(client):
    """Verify GET /notes?tag=... works."""
    client.post("/notes", json={"title": "Work Note", "tags": ["work", "important"]})
    client.post("/notes", json={"title": "Home Note", "tags": ["home"]})
    
    res = client.get("/notes?tag=work")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Work Note"

def test_update_note_tags(client):
    """Verify updating tags for an existing note."""
    post_res = client.post("/notes", json={"title": "Idea", "tags": ["draft"]})
    note_id = post_res.get_json()["id"]
    
    res = client.put(f"/notes/{note_id}", json={"tags": ["final"]})
    assert res.status_code == 200
    assert res.get_json()["tags"] == ["final"]

def test_note_timestamps(client):
    """Verify created_at and updated_at are set."""
    res = client.post("/notes", json={"title": "Timestamps"})
    assert res.status_code == 201
    data = res.get_json()
    assert "created_at" in data
    assert "updated_at" in data
    
    # Update note to check updated_at changes
    note_id = data["id"]
    put_res = client.put(f"/notes/{note_id}", json={"title": "Timestamps Updated"})
    assert put_res.status_code == 200
    update_data = put_res.get_json()
    assert update_data["updated_at"] != update_data["created_at"]
    assert update_data["created_at"] == data["created_at"]

def test_due_date_and_overdue(client):
    """Verify due_date is saved and overdue query fetching works."""
    from datetime import datetime, timezone, timedelta
    
    now = datetime.now(timezone.utc)
    past = (now - timedelta(days=2)).isoformat()
    future = (now + timedelta(days=2)).isoformat()
    
    # Create notes
    client.post("/notes", json={"title": "Overdue Note", "due_date": past})
    client.post("/notes", json={"title": "Future Note", "due_date": future})
    client.post("/notes", json={"title": "No Due Date"})
    
    res = client.get("/notes?overdue=true")
    assert res.status_code == 200
    data = res.get_json()
    
    # Depending on previous test state, we might have multiple, but filter to ones we just made
    overdue_notes = [n for n in data if n["title"] == "Overdue Note"]
    future_notes = [n for n in data if n["title"] == "Future Note"]
    
    assert len(overdue_notes) == 1
    assert len(future_notes) == 0