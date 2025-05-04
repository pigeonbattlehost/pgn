from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

players = {}  # UUID -> dict with player info

@app.route('/ping', methods=['POST'])
def ping():
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id or player_id not in players:
        # Новый игрок заходит — генерируем UUID
        new_id = str(uuid.uuid4())
        players[new_id] = {"last_seen": time.time(), "status": "waiting", "state": {}}
    else:
        # Для существующего игрока обновляем время последнего посещения
        now = time.time()
        players[player_id]["last_seen"] = now

    # Подсчитываем количество онлайн пижонов за последние 40 секунд
    now = time.time()
    online_count = sum(1 for p in players.values() if now - p["last_seen"] <= 40)

    return jsonify(online_count), 200

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
    data = request.get_json()  # Данные от клиента
    player_id = data.get("player_id")
    state = data.get("state")  # Состояние игрока, например позиция, хп, и т.д.

    if player_id not in players:
        return jsonify({"error": "Player not found"}), 400

    players[player_id]["last_seen"] = time.time()
    players[player_id]["state"] = state

    # Логируем полученные данные
    print(f"Sync received for player {player_id}: {state}")

    # Возвращаем состояние других игроков
    now = time.time()
    visible = {
        pid: pdata["state"]
        for pid, pdata in players.items()
        if pid != player_id and now - pdata["last_seen"] < 10
    }

    print(f"Visible players for {player_id}: {visible}")

    return jsonify({"others": visible}), 200

if __name__ == '__main__':
    app.run(debug=True)