from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)

# Разрешаем CORS для всех доменов
CORS(app)

pigeons = {}

@app.route("/ping", methods=["POST"])
def ping():
    pigeons[request.remote_addr] = time.time()
    return jsonify({"status": "pinged"})

@app.route("/multiplayer", methods=["GET"])
def multiplayer():
    now = time.time()
    online = [ip for ip, t in pigeons.items() if now - t <= 30]
    if len(online) > 1:
        return jsonify({"status": "ready", "players": online[:2]})
    return jsonify({"status": "waiting", "message": "Not enough pigeons!"})

@app.route("/update_position", methods=["POST"])
def update_position():
    data = request.json
    pigeons[request.remote_addr] = data
    return jsonify({"status": "position_updated"})

@app.route("/shoot", methods=["POST"])
def shoot():
    pigeons[request.remote_addr]["shooting"] = True
    return jsonify({"status": "shooting"})

@app.route("/stop_shooting", methods=["POST"])
def stop_shooting():
    pigeons[request.remote_addr]["shooting"] = False
    return jsonify({"status": "stopped_shooting"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)