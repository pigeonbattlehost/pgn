from flask import Flask, request, jsonify
import uuid
import time

app = Flask(__name__)

# Словарь для хранения данных о пижонах
pigeons = {}

# Шифрование UUID
def encrypt_uuid(player_id):
    return player_id  # Просто возвращаем для простоты, можешь добавить шифрование, если нужно

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

@app.route("/update_position", methods=["POST"])
def update_position():
    data = request.json
    player_id = data.get("player_id")
    x = data.get("x")
    y = data.get("y")

    if player_id and x is not None and y is not None:
        pigeons[player_id]["x"] = x
        pigeons[player_id]["y"] = y
        return jsonify({"status": "position_updated"})

    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route("/multiplayer", methods=["GET"])
def multiplayer_status():
    current_time = time.time()
    online_pigeons = {pid: pdata for pid, pdata in pigeons.items() if current_time - pdata["last_ping"] <= 5}

    if len(online_pigeons) >= 2:
        return jsonify({"status": "ready", "players": list(online_pigeons.keys())})
    else:
        return jsonify({"status": "waiting"})

if __name__ == "__main__":
    app.run(debug=True)