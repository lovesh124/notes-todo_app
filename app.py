from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory store for simplicity (suitable for demo/tests)
NOTES = {}
NEXT_ID = 1


@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Notes & Todo API"})


@app.route("/notes", methods=["GET"])
def list_notes():
    return jsonify(list(NOTES.values())), 200


@app.route("/notes", methods=["POST"])
def create_note():
    global NEXT_ID
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    note = {
        "id": NEXT_ID,
        "title": data.get("title"),
        "content": data.get("content", ""),
        "done": bool(data.get("done", False)),
    }

    NOTES[NEXT_ID] = note
    NEXT_ID += 1
    return jsonify(note), 201


@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id: int):
    note = NOTES.get(note_id)
    if not note:
        return jsonify({"error": "not found"}), 404
    return jsonify(note), 200


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id: int):
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid payload"}), 400

    note = NOTES.get(note_id)
    if not note:
        return jsonify({"error": "not found"}), 404

    note["title"] = data.get("title", note["title"])
    note["content"] = data.get("content", note["content"])
    note["done"] = bool(data.get("done", note["done"]))

    NOTES[note_id] = note
    return jsonify(note), 200


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id: int):
    if note_id in NOTES:
        del NOTES[note_id]
        return "", 204
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
