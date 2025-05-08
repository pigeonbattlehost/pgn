from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time
import sqlite3
import hashlib

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

players = {}  # UUID -> dict with player info

# global variable for storing pigeons spend
pigeon_fund = 0

@app.route('/ping', methods=['POST'])
def ping():
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id or player_id not in players:
        # uuid gen
        new_id = str(uuid.uuid4())
        players[new_id] = {"last_seen": time.time(), "status": "waiting", "state": {}, "spent_coins": 0}
    else:
        now = time.time()
        players[player_id]["last_seen"] = now

    # counting online
    now = time.time()
    online_count = sum(1 for p in players.values() if now - p["last_seen"] <= 40)

    return jsonify(online_count), 200

@app.route('/multiplayerPing', methods=['GET'])
def multiplayer_ping():
    player_id = request.args.get('player_id')

    if not player_id or player_id not in players:
        
        new_id = str(uuid.uuid4())
        players[new_id] = {"last_seen": time.time(), "status": "waiting", "state": {}, "spent_coins": 0}
        return jsonify({
            "status": "online",
            "message": "New player created",
            "player_id": new_id
        }), 201

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

@app.route('/updateSpentCoins', methods=['POST'])
def update_spent_coins():
    global pigeon_fund
    data = request.get_json()
    player_id = data.get('player_id')
    amount = data.get('amount')

    if not player_id or player_id not in players:
        return jsonify({"error": "Player not found"}), 400

    if amount is None or not isinstance(amount, int) or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    players[player_id]["spent_coins"] += amount
    pigeon_fund += amount  # <-- ЭТО ДОБАВЬ, иначе фонд не растёт!

    return jsonify({
        "message": f"Spent {amount} coins",
        "spent_coins": players[player_id]["spent_coins"],
        "total_fund": pigeon_fund
    }), 200

# Роут для получения потраченных коинов
@app.route('/getSpentCoins', methods=['GET'])
def get_spent_coins():
    player_id = request.args.get('player_id')

    if not player_id or player_id not in players:
        return jsonify({"error": "Player not found"}), 400

    spent_coins = players[player_id]["spent_coins"]
    return jsonify({"spent_coins": spent_coins}), 200

@app.route('/getTotalFund', methods=['GET'])
def get_total_fund():
    return jsonify({"pigeon_fund": pigeon_fund}), 200

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('pigeon_battle.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Функция для хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Хешируем пароль перед сохранением
    hashed_password = hash_password(password)

    conn = sqlite3.connect('pigeon_battle.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully!'})

# Логин пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Хешируем введённый пароль
    hashed_password = hash_password(password)

    conn = sqlite3.connect('pigeon_battle.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401

if __name__ == '__main__':
    app.run(debug=True)