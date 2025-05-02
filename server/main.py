
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time

app = Flask(__name__)
CORS(app)

# Словарь: UUID -> последнее время пинга
players = {}

@app.route('/ping', methods=['POST'])
def ping():
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id:
        # Новый игрок — выдаём UUID
        new_id = str(uuid.uuid4())
        players[new_id] = time.time()
        return jsonify({"player_id": new_id}), 201

    # Обновляем пинг
    players[player_id] = time.time()
    return jsonify({"status": "pong", "player_id": player_id}), 200

@app.route('/players', methods=['GET'])
def get_players():
    # Возвращает список всех активных игроков за последние 10 секунд
    now = time.time()
    active_players = [pid for pid, last_seen in players.items() if now - last_seen < 10]
    return jsonify({"active_players": active_players}), 200


@app.route('/match', methods=['POST'])
def match():
    player_id = request.json.get('player_id')
    
    if not player_id or player_id not in players:
        return jsonify({"error": "Player not found"}), 400

    # Ищем доступного противника
    opponent_id = None
    for pid, data in players.items():
        if pid != player_id and data["status"] == "waiting":
            opponent_id = pid
            players[pid]["status"] = "matched"
            players[player_id]["status"] = "matched"
            break
    
    if opponent_id:
        return jsonify({"message": "Opponent found", "opponent_id": opponent_id}), 200
    else:
        return jsonify({"message": "No opponent found, please wait..."}), 200

if __name__ == '__main__':
    app.run(debug=True)