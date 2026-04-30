import pytest

import app as app_module


@pytest.fixture(autouse=True)
def reset_state():
    # Ensure a clean in-memory store between tests
    app_module.NOTES.clear()
    app_module.NEXT_ID = 1


@pytest.fixture
def client():
    app_module.app.testing = True
    with app_module.app.test_client() as client:
        yield client


def test_create_note(client):
    res = client.post("/notes", json={"title": "First", "content": "hello"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] == 1
    assert data["title"] == "First"


def test_get_notes(client):
    client.post("/notes", json={"title": "x"})
    res = client.get("/notes")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_note(client):
    client.post("/notes", json={"title": "a", "content": "b"})
    res = client.get("/notes/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == 1


def test_update_note(client):
    client.post("/notes", json={"title": "a"})
    res = client.put("/notes/1", json={"title": "updated", "done": True})
    assert res.status_code == 200
    data = res.get_json()
    assert data["title"] == "updated"
    assert data["done"] is True


def test_delete_note(client):
    client.post("/notes", json={"title": "a"})
    res = client.delete("/notes/1")
    assert res.status_code == 204
    res2 = client.get("/notes/1")
    assert res2.status_code == 404


def test_create_without_title(client):
    res = client.post("/notes", json={"content": "no title"})
    assert res.status_code == 400


def test_get_nonexistent_note(client):
    """Verify 404 for missing resources"""
    res = client.get("/notes/999")
    assert res.status_code == 404

def test_update_nonexistent_note(client):
    """Verify 404 when updating missing resources"""
    res = client.put("/notes/999", json={"title": "Ghost"})
    assert res.status_code == 404

def test_delete_nonexistent_note(client):
    """Verify 404 when deleting missing resources"""
    res = client.delete("/notes/999")
    assert res.status_code == 404

def test_malformed_json_post(client):
    """Verify 400 for bad payloads"""
    res = client.post("/notes", data="not json", content_type='application/json')
    assert res.status_code == 400