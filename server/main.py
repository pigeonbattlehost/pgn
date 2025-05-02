from flask import Flask, request, jsonify
from flask_cors import CORS  # Импортируем CORS

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всего приложения

pigeons = {}

@app.route("/ping", methods=["POST"])
def ping():
    ip = request.remote_addr
    pigeons[ip] = time.time()
    return jsonify({"status": "pinged"})

@app.route("/pigeons_online", methods=["GET"])
def get_online_pigeons():
    now = time.time()
    online = [ip for ip, t in pigeons.items() if now - t <= 30]
    return jsonify({"pigeons_online": len(online)})

@app.route("/")
def home():
    return "Pigeon Server is running!"