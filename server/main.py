from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всего приложения

pigeons = {}  # Здесь будут храниться данные о пижонах и их состоянии

@app.route("/ping", methods=["POST"])
def ping():
    ip = request.remote_addr
    pigeons[ip] = {
        "last_ping": time.time(),
        "x": 0,  # начальная позиция игрока по оси X
        "y": 0,  # начальная позиция игрока по оси Y
        "shooting": False  # начальное состояние, не стреляет
    }
    return jsonify({"status": "pinged"})

@app.route("/", methods=["GET"])
def home():
    now = time.time()
    # Считаем тех, кто пинговал за последние 30 секунд
    online = [ip for ip, t in pigeons.items() if now - t["last_ping"] <= 30]
    return jsonify({"pigeons_online": len(online)})

@app.route("/multiplayer", methods=["GET"])
def multiplayer():
    now = time.time()
    online = [ip for ip, t in pigeons.items() if now - t["last_ping"] <= 30]
    if len(online) > 1:  # Если хотя бы 2 пижона онлайн
        return jsonify({"status": "ready", "players": online})
    else:
        return jsonify({"status": "waiting", "message": "Not enough pigeons online to play!"})

@app.route("/update_position", methods=["POST"])
def update_position():
    ip = request.remote_addr
    data = request.json
    if ip in pigeons:
        pigeons[ip]["x"] = data.get("x", pigeons[ip]["x"])
        pigeons[ip]["y"] = data.get("y", pigeons[ip]["y"])
    return jsonify({"status": "position_updated", "x": pigeons[ip]["x"], "y": pigeons[ip]["y"]})

@app.route("/shoot", methods=["POST"])
def shoot():
    ip = request.remote_addr
    if ip in pigeons:
        pigeons[ip]["shooting"] = True
    return jsonify({"status": "shooting", "shooting": pigeons[ip]["shooting"]})

@app.route("/stop_shooting", methods=["POST"])
def stop_shooting():
    ip = request.remote_addr
    if ip in pigeons:
        pigeons[ip]["shooting"] = False
    return jsonify({"status": "stopped_shooting", "shooting": pigeons[ip]["shooting"]})


@app.route('/findEnemy', methods=['GET'])
def debug_get():
    return "Server is alive"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)