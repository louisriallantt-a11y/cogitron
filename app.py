import os
import sqlite3
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026'

# --- GESTION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# --- CONFIGURATION LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_db_connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             username TEXT UNIQUE, password TEXT, 
                             color TEXT DEFAULT '#00ff88', 
                             is_admin INTEGER DEFAULT 0,
                             is_banned INTEGER DEFAULT 0)''')
            conn.commit()
        print("Base de données SQLite prête.")
    except Exception as e:
        print(f"CRASH INIT_DB : {e}")

# Lancement immédiat
init_db()

class User(UserMixin):
    def __init__(self, id, username, color, is_admin, is_banned):
        self.id, self.username, self.color, self.is_admin, self.is_banned = id, username, color, is_admin, is_banned

@login_manager.user_loader
def load_user(user_id):
    try:
        with get_db_connection() as conn:
            u = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            if u: return User(u['id'], u['username'], u['color'], u['is_admin'], u['is_banned'])
    except: return None
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        u, p = data.get('username'), data.get('password')
        with get_db_connection() as conn:
            count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            is_admin = 1 if count == 0 else 0
            conn.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                         (u, generate_password_hash(p), is_admin))
            conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Pseudo déjà pris ou erreur."}), 400

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
            if user and check_password_hash(user['password'], data['password']):
                if user['is_banned']: 
                    return jsonify({"status": "error", "message": "Compte banni."}), 403
                login_user(User(user['id'], user['username'], user['color'], user['is_admin'], user['is_banned']))
                return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Identifiants invalides."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": "Erreur serveur."}), 500

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        msg = request.json.get('message')
        reponse = ia_repond(msg, current_user.username)
        return jsonify({"reponse": reponse})
    except Exception as e:
        return jsonify({"reponse": "L'IA est indisponible pour le moment."}), 200

@app.route('/admin_stats')
@login_required
def admin_stats():
    if not current_user.is_admin: return jsonify({"error": "Interdit"}), 403
    with get_db_connection() as conn:
        users = conn.execute('SELECT id, username, is_admin, is_banned FROM users').fetchall()
        return jsonify({"users": [dict(u) for u in users]})

@app.route('/ban/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    if not current_user.is_admin: return jsonify({"error": "Interdit"}), 403
    with get_db_connection() as conn:
        conn.execute('UPDATE users SET is_banned = 1 WHERE id = ?', (user_id,))
        conn.commit()
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
