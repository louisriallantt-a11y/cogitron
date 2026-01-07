import os, sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-2026'

DB_PATH = 'database.db'
login_manager = LoginManager(app)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, is_admin INTEGER, is_banned INTEGER DEFAULT 0)')

class User(UserMixin):
    def __init__(self, id, username, is_admin):
        self.id, self.username, self.is_admin = id, username, is_admin

@login_manager.user_loader
def load_user(uid):
    with get_db() as conn:
        u = conn.execute('SELECT * FROM users WHERE id = ?', (uid,)).fetchone()
        return User(u['id'], u['username'], u['is_admin']) if u else None

@app.route('/')
def index(): return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = data.get('username')
    is_admin = 1 if user == "Louis Riallant" else 0
    with get_db() as conn:
        try:
            conn.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                         (user, generate_password_hash(data.get('password')), is_admin))
            conn.commit()
        except: pass
    return jsonify({"status": "ok"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with get_db() as conn:
        u = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
        if u and check_password_hash(u['password'], data['password']):
            login_user(User(u['id'], u['username'], u['is_admin']))
            session['history'] = []
            return jsonify({"status": "ok", "is_admin": u['is_admin']})
    return jsonify({"status": "err"}), 401

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json.get('message')
    hist = session.get('history', [])
    hist.append({"role": "user", "content": msg})
    resp = ia_repond(hist, current_user.username)
    hist.append({"role": "assistant", "content": resp})
    session['history'] = hist[-10:]
    return jsonify({"reponse": resp})

@app.route('/admin_data')
@login_required
def admin_data():
    if not current_user.is_admin: return jsonify([]), 403
    with get_db() as conn:
        users = conn.execute('SELECT id, username, is_admin FROM users').fetchall()
        return jsonify({"users": [dict(u) for u in users]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
