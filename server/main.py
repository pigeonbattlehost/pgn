from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time

app = Flask(__name__)
CORS(app)

players = {}  # UUID -> dict with player info

@app.route('/ping', methods=['POST'])
def ping():
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id or player_id not in players:
        # New player joins — generate UUID
        new_id = str(uuid.uuid4())
        players[new_id] = {"last_seen": time.time(), "status": "waiting", "state": {}}
        return jsonify({"player_id": new_id}), 201

    # also returning latest count of pigeons for 40 sec
    now = time.time()
    online_count = sum(1 for p in players.values() if now - p["last_seen"] <= 40)

    players[player_id]["last_seen"] = now
    return jsonify({
        "status": "pong",
        "player_id": player_id,
        "pigeons_online": online_count
    }), 200

@app.route('/multiplayerPing', methods=['GET'])
def multiplayer_ping():
    player_id = request.args.get('player_id')

    if not player_id or player_id not in players:
        # New player — generate UUID
        new_id = str(uuid.uuid4())
        players[new_id] = {"last_seen": time.time(), "status": "waiting", "state": {}}
        return jsonify({
            "status": "online",
            "message": "New player created",
            "player_id": new_id
        }), 201

    # Existing player — just update activity
    players[player_id]["last_seen"] = time.time()
    return jsonify({
        "status": "online",
        "message": "Player already active",
        "player_id": player_id
    }), 200

@app.route('/match', methods=['POST'])
def match():
    player_id = request.json.get('player_id')

    if not player_id or player_id not in players:
        return jsonify({"error": "Player not found"}), 400

    opponent_id = None
    for pid, pdata in players.items():
        if pid != player_id and pdata["status"] == "waiting":
            opponent_id = pid
            players[pid]["status"] = "matched"
            players[player_id]["status"] = "matched"
            break

    if opponent_id:
        return jsonify({"message": "Opponent found", "opponent_id": opponent_id}), 200
    else:
        return jsonify({"message": "No opponent found, please wait..."}), 200

@app.route('/sync', methods=['POST'])
def sync():
    data = request.get_json()
    player_id = data.get("player_id")
    state = data.get("state")  # position, angle, hp, etc.

    if player_id not in players:
        return jsonify({"error": "Player not found"}), 400

    players[player_id]["last_seen"] = time.time()
    players[player_id]["state"] = state

    # Return state of other players (excluding self)
    now = time.time()
    visible = {
        pid: pdata["state"]
        for pid, pdata in players.items()
        if pid != player_id and now - pdata["last_seen"] < 10
    }

    return jsonify({"others": visible}), 200

if __name__ == '__main__':
    app.run(debug=True)