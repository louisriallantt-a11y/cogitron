import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026-secure'

# --- BASE DE DONNÉES ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        # Table Users étendue
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         username TEXT UNIQUE, password TEXT, 
                         color TEXT DEFAULT "#00ff88", 
                         is_admin INTEGER DEFAULT 0, 
                         is_banned INTEGER DEFAULT 0)''')
        # Table Messages pour historique
        conn.execute('''CREATE TABLE IF NOT EXISTS messages 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                         content TEXT, role TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        # Table Suggestions (Boîte à idées)
        conn.execute('''CREATE TABLE IF NOT EXISTS suggestions 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, idea TEXT)''')
        conn.commit()
init_db()

# --- GESTION DES SESSIONS ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

class User(UserMixin):
    def __init__(self, id, username, color, is_admin, is_banned):
        self.id = id
        self.username = username
        self.color = color
        self.is_admin = is_admin
        self.is_banned = is_banned

@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        u = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if u: return User(u['id'], u['username'], u['color'], u['is_admin'], u['is_banned'])
    return None

# --- ROUTES AUTH ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    u, p = data.get('username'), data.get('password')
    colors = ["#00ff88", "#00d1ff", "#ff007a", "#ffcc00", "#9d00ff"]
    import random
    with get_db_connection() as conn:
        count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        is_admin = 1 if count == 0 else 0
        try:
            conn.execute('INSERT INTO users (username, password, color, is_admin) VALUES (?, ?, ?, ?)',
                         (u, generate_password_hash(p), random.choice(colors), is_admin))
            conn.commit()
            return jsonify({"status": "success"})
        except: return jsonify({"message": "Nom indisponible"}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
            if user and check_password_hash(user['password'], data['password']):
                if user['is_banned']: return jsonify({"message": "ACCÈS REFUSÉ : VOUS ÊTES BANNI"}), 403
                login_user(User(user['id'], user['username'], user['color'], user['is_admin'], user['is_banned']))
                return jsonify({"status": "success"})
        return jsonify({"message": "Identifiants incorrects"}), 401
    return redirect(url_for('index'))

# --- ROUTES CHAT & SUGGESTIONS ---
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json['message']
    reponse = ia_repond(msg, current_user.username)
    with get_db_connection() as conn:
        conn.execute('INSERT INTO messages (user_id, content, role) VALUES (?, ?, ?)', (current_user.id, msg, 'user'))
        conn.execute('INSERT INTO messages (user_id, content, role) VALUES (?, ?, ?)', (current_user.id, reponse, 'ia'))
        conn.commit()
    return jsonify({"reponse": reponse})

@app.route('/suggest', methods=['POST'])
@login_required
def suggest():
    idea = request.json.get('idea')
    with get_db_connection() as conn:
        conn.execute('INSERT INTO suggestions (username, idea) VALUES (?, ?)', (current_user.username, idea))
        conn.commit()
    return jsonify({"status": "success"})

@app.route('/get_history')
@login_required
def get_history():
    with get_db_connection() as conn:
        msgs = conn.execute('SELECT content, role FROM messages WHERE user_id = ? ORDER BY timestamp ASC', (current_user.id,)).fetchall()
        return jsonify([dict(m) for m in msgs])

# --- ROUTES ADMIN ---
@app.route('/admin_stats')
@login_required
def admin_stats():
    if not current_user.is_admin: return jsonify({"error": "Interdit"}), 403
    with get_db_connection() as conn:
        users = conn.execute('SELECT username, is_admin, is_banned FROM users').fetchall()
        suggs = conn.execute('SELECT username, idea FROM suggestions').fetchall()
        return jsonify({"users": [dict(u) for u in users], "suggestions": [dict(s) for s in suggs]})

@app.route('/admin_action', methods=['POST'])
@login_required
def admin_action():
    if not current_user.is_admin: return jsonify({"error": "Interdit"}), 403
    data = request.json
    action, target = data.get('action'), data.get('target')
    with get_db_connection() as conn:
        if action == 'ban': conn.execute('UPDATE users SET is_banned = 1 WHERE username = ?', (target,))
        elif action == 'unban': conn.execute('UPDATE users SET is_banned = 0 WHERE username = ?', (target,))
        elif action == 'promote': conn.execute('UPDATE users SET is_admin = 1 WHERE username = ?', (target,))
        conn.commit()
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    logout_user(); return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
