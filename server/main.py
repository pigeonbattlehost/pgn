from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всего приложения

pigeons = {}

@app.route("/ping", methods=["POST"])
def ping():
    ip = request.remote_addr
    pigeons[ip] = time.time()
    return jsonify({"status": "pinged"})

@app.route("/", methods=["GET"])
def home():
    now = time.time()
    # Считаем тех, кто пинговал за последние 30 секунд
    online = [ip for ip, t in pigeons.items() if now - t <= 30]
    return jsonify({"pigeons_online": len(online)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)