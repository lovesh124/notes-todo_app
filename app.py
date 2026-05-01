from flask import Flask, jsonify, request
from db import get_database, COLLECTION_NAME
from bson.objectid import ObjectId

app = Flask(__name__)

def serialize_note(note):
    """Convert MongoDB _id to string id for JSON serialization."""
    if not note:
        return None
    note["id"] = str(note.pop("_id"))
    return note

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Notes & Todo API"})


@app.route("/notes", methods=["GET"])
def list_notes():
    db = get_database()
    collection = db[COLLECTION_NAME]
    
    query = {}
    tag = request.args.get("tag")
    if tag:
        query["tags"] = tag
        
    notes = [serialize_note(note) for note in collection.find(query)]
    return jsonify(notes), 200


@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    note = {
        "title": data.get("title"),
        "content": data.get("content", ""),
        "done": bool(data.get("done", False)),
        "tags": data.get("tags", []),
    }
    
    db = get_database()
    collection = db[COLLECTION_NAME]
    result = collection.insert_one(note)
    
    note["_id"] = result.inserted_id
    return jsonify(serialize_note(note)), 201


@app.route("/notes/<note_id>", methods=["GET"])
def get_note(note_id: str):
    db = get_database()
    collection = db[COLLECTION_NAME]
    
    try:
        note = collection.find_one({"_id": ObjectId(note_id)})
        if not note:
            return jsonify({"error": "not found"}), 404
        return jsonify(serialize_note(note)), 200
    except Exception:
        return jsonify({"error": "invalid id format"}), 400


@app.route("/notes/<note_id>", methods=["PUT"])
def update_note(note_id: str):
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid payload"}), 400

    db = get_database()
    collection = db[COLLECTION_NAME]
    
    update_data = {}
    if "title" in data:
        update_data["title"] = data["title"]
    if "content" in data:
        update_data["content"] = data["content"]
    if "done" in data:
        update_data["done"] = bool(data["done"])
    if "tags" in data and isinstance(data["tags"], list):
        update_data["tags"] = data["tags"]
        
    try:
        result = collection.update_one({"_id": ObjectId(note_id)}, {"$set": update_data})
        if result.matched_count == 0:
            return jsonify({"error": "not found"}), 404
            
        note = collection.find_one({"_id": ObjectId(note_id)})
        return jsonify(serialize_note(note)), 200
    except Exception:
        return jsonify({"error": "invalid id format"}), 400


@app.route("/notes/<note_id>", methods=["DELETE"])
def delete_note(note_id: str):
    db = get_database()
    collection = db[COLLECTION_NAME]
    
    try:
        result = collection.delete_one({"_id": ObjectId(note_id)})
        if result.deleted_count > 0:
            return "", 204
        return jsonify({"error": "not found"}), 404
    except Exception:
        return jsonify({"error": "invalid id format"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)