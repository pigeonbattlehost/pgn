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

@app.route('/findEnemy', methods=['POST'])
def find_enemy():
    data = request.get_json() or {}
    player_ip = request.remote_addr   # Client IP address3
    player_hp = data.get('hp')
    selected_pigeon = data.get('pigeon')

    # Initialize or update this player's info
    if player_ip not in players or players[player_ip]['state'] != 'matched':
        # (Re)register as waiting with latest HP/pigeon
        players[player_ip] = {
            'hp': player_hp,
            'pigeon': selected_pigeon,
            'state': 'waiting',
            'opponent': None
        }

    # If already matched (race condition or repeat call), return existing match info
    if players[player_ip]['state'] == 'matched':
        opp_ip = players[player_ip]['opponent']
        opp_info = players.get(opp_ip, {})
        return jsonify(status="match_found", opponent={
            "ip": opp_ip,
            "hp": opp_info.get('hp'),
            "pigeon": opp_info.get('pigeon')
        })

    # Attempt to find a waiting opponent
    for opp_ip, info in players.items():
        if opp_ip == player_ip:
            continue
        if info['state'] == 'waiting' and abs(info['hp'] - player_hp) <= 1000:
            # Match found: update both players to 'matched'
            players[player_ip]['state'] = 'matched'
            players[player_ip]['opponent'] = opp_ip
            players[opp_ip]['state'] = 'matched'
            players[opp_ip]['opponent'] = player_ip
            # Respond with opponent info
            return jsonify(status="match_found", opponent={
                "ip": opp_ip,
                "hp": info['hp'],
                "pigeon": info['pigeon']
            })

    # No opponent: remain waiting
    return jsonify(status="waiting")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)