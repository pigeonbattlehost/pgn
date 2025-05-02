import uuid
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)

# Разрешаем CORS для всех доменов
CORS(app)

pigeons = {}  # Хранение игроков по уникальному ID

def encrypt_uuid(player_id):
    return hashlib.sha256(player_id.encode('utf-8')).hexdigest()

@app.route("/ping", methods=["POST"])
def ping():
    player_id = request.json.get("player_id")
    if not player_id:
        player_id = str(uuid.uuid4())

    # Шифруем UUID
    encrypted_id = encrypt_uuid(player_id)

    # Обновляем время последнего пинга для этого пижона
    pigeons[encrypted_id] = {"last_ping": time.time()}

    # Считаем пижонов, которые пинговали за последние 5 секунд
    current_time = time.time()
    online_count = sum(1 for p in pigeons.values() if current_time - p["last_ping"] <= 5)

    return jsonify({
        "status": "pinged",
        "player_id": encrypted_id,
        "pigeons_online": online_count
    })

@app.route("/multiplayer", methods=["GET"])
def multiplayer():
    now = time.time()
    online = [player_id for player_id, data in pigeons.items() if now - data["last_ping"] <= 30]  # Игроки, активные в последние 30 секунд
    
    if len(online) > 1:
        return jsonify({"status": "ready", "players": online[:1]})
    return jsonify({"status": "waiting", "message": "Not enough pigeons!"})

@app.route("/update_position", methods=["POST"])
def update_position():
    data = request.json
    player_id = data.get("player_id")
    
    if not player_id:
        return jsonify({"status": "error", "message": "Player ID missing"}), 400

    # Шифруем UUID
    encrypted_id = encrypt_uuid(player_id)

    if encrypted_id not in pigeons:
        return jsonify({"status": "error", "message": "Player not found"}), 404

    # Обновляем позицию игрока
    pigeons[encrypted_id]["position"] = data
    return jsonify({"status": "position_updated"})

@app.route("/shoot", methods=["POST"])
def shoot():
    data = request.json
    player_id = data.get("player_id")

    if not player_id:
        return jsonify({"status": "error", "message": "Player ID missing"}), 400

    # Шифруем UUID
    encrypted_id = encrypt_uuid(player_id)

    if encrypted_id not in pigeons:
        return jsonify({"status": "error", "message": "Player not found"}), 404

    pigeons[encrypted_id]["shooting"] = True
    return jsonify({"status": "shooting"})

@app.route("/stop_shooting", methods=["POST"])
def stop_shooting():
    data = request.json
    player_id = data.get("player_id")

    if not player_id:
        return jsonify({"status": "error", "message": "Player ID missing"}), 400

    # Шифруем UUID
    encrypted_id = encrypt_uuid(player_id)

    if encrypted_id not in pigeons:
        return jsonify({"status": "error", "message": "Player not found"}), 404

    pigeons[encrypted_id]["shooting"] = False
    return jsonify({"status": "stopped_shooting"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)