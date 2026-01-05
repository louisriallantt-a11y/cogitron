import os
import sqlite3
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-full-power-2026'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        # Table utilisateurs
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, color TEXT DEFAULT "#00ff88")')
        # Table messages pour la mémoire
        conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, role TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
        conn.commit()
init_db()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

class User(UserMixin):
    def __init__(self, id, username, color):
        self.id = id
        self.username = username
        self.color = color

@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user: return User(user['id'], user['username'], user['color'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    colors = ["#00ff88", "#00d1ff", "#ff007a", "#ffcc00", "#9d00ff"]
    import random
    hashed_pw = generate_password_hash(data['password'])
    try:
        with get_db_connection() as conn:
            conn.execute('INSERT INTO users (username, password, color) VALUES (?, ?, ?)', 
                         (data['username'], hashed_pw, random.choice(colors)))
            conn.commit()
        return jsonify({"status": "success"})
    except: return jsonify({"message": "Nom déjà pris"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
        if user and check_password_hash(user['password'], data['password']):
            login_user(User(user['id'], user['username'], user['color']))
            return jsonify({"status": "success"})
    return jsonify({"message": "Erreur"}), 401

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json['message']
    # 1. Sauver message utilisateur
    with get_db_connection() as conn:
        conn.execute('INSERT INTO messages (user_id, content, role) VALUES (?, ?, ?)', (current_user.id, msg, 'user'))
        conn.commit()
    
    # 2. Réponse IA
    reponse = ia_repond(msg, current_user.username)
    
    # 3. Sauver message IA
    with get_db_connection() as conn:
        conn.execute('INSERT INTO messages (user_id, content, role) VALUES (?, ?, ?)', (current_user.id, reponse, 'ia'))
        conn.commit()
        
    return jsonify({"reponse": reponse})

@app.route('/get_history')
@login_required
def get_history():
    with get_db_connection() as conn:
        msgs = conn.execute('SELECT content, role FROM messages WHERE user_id = ? ORDER BY timestamp ASC', (current_user.id,)).fetchall()
        return jsonify([dict(m) for m in msgs])

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
