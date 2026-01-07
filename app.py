import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026'

# --- BASE DE DONNEES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         username TEXT UNIQUE, password TEXT, 
                         color TEXT DEFAULT '#00ff88', 
                         is_admin INTEGER DEFAULT 0,
                         is_banned INTEGER DEFAULT 0)''')
        conn.commit()

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

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        with get_db_connection() as conn:
            count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            is_admin = 1 if count == 0 else 0
            conn.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                         (data['username'], generate_password_hash(data['password']), is_admin))
            conn.commit()
        return jsonify({"status": "success"})
    except: return jsonify({"status": "error"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
        if user and check_password_hash(user['password'], data['password']):
            if user['is_banned']: return jsonify({"status": "error"}), 403
            login_user(User(user['id'], user['username'], user['color'], user['is_admin'], user['is_banned']))
            return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 401

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json.get('message')
    reponse = ia_repond(msg, current_user.username)
    return jsonify({"reponse": reponse})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
