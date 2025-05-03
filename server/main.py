from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time

app = Flask(__name__)
CORS(app)

players = {}  # UUID -> dict с инфой

@app.route('/ping', methods=['POST'])
def ping():
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id or player_id not in players:
        # Новый игрок — выдаём UUID
        new_id = str(uuid.uuid4())
        players[new_id] = {"last_seen": time.time(), "status": "waiting", "state": {}}
        return jsonify({"player_id": new_id}), 201

    players[player_id]["last_seen"] = time.time()
    return jsonify({"status": "pong", "player_id": player_id}), 200

@app.route('/players', methods=['GET'])
def get_players():
    now = time.time()
    active_players = [pid for pid, p in players.items() if now - p["last_seen"] < 10]
    return jsonify({"active_players": active_players}), 200

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
    state = data.get("state")  # позиция, угол, хп, всё что надо

    if player_id not in players:
        return jsonify({"error": "Player not found"}), 400

    players[player_id]["last_seen"] = time.time()
    players[player_id]["state"] = state

    # Отдаём инфу о других игроках (без него самого)
    now = time.time()
    visible = {
        pid: pdata["state"]
        for pid, pdata in players.items()
        if pid != player_id and now - pdata["last_seen"] < 10
    }

    return jsonify({"others": visible}), 200

if __name__ == '__main__':
    app.run(debug=True)