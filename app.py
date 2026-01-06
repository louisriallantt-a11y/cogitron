import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026'

# --- CONFIG LOGIN MANAGER ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

# --- CONNEXION SUPABASE ---
def get_db_connection():
    # Utilise l'URL que tu as mise dans les variables d'environnement sur Render
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id SERIAL PRIMARY KEY, 
                             username TEXT UNIQUE, password TEXT, 
                             color TEXT DEFAULT '#00ff88', 
                             is_admin INTEGER DEFAULT 0, 
                             is_banned INTEGER DEFAULT 0)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS messages 
                            (id SERIAL PRIMARY KEY, user_id INTEGER, 
                             content TEXT, role TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS suggestions 
                            (id SERIAL PRIMARY KEY, username TEXT, idea TEXT)''')
            conn.commit()
init_db()

class User(UserMixin):
    def __init__(self, id, username, color, is_admin, is_banned):
        self.id = id
        self.username = username
        self.color = color
        self.is_admin = is_admin
        self.is_banned = is_banned

@login_manager.user_loader
def load_user(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                u = cur.fetchone()
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
    u, p = data.get('username'), data.get('password')
    import random
    color = random.choice(["#00ff88", "#00d1ff", "#ff007a", "#ffcc00", "#9d00ff"])
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM users')
            is_admin = 1 if cur.fetchone()[0] == 0 else 0
            try:
                cur.execute('INSERT INTO users (username, password, color, is_admin) VALUES (%s, %s, %s, %s)',
                             (u, generate_password_hash(p), color, is_admin))
                conn.commit()
                return jsonify({"status": "success"})
            except: return jsonify({"message": "Nom déjà pris"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM users WHERE username = %s', (data['username'],))
            user = cur.fetchone()
            if user and check_password_hash(user['password'], data['password']):
                if user['is_banned']: return jsonify({"message": "BANNI"}), 403
                login_user(User(user['id'], user['username'], user['color'], user['is_admin'], user['is_banned']))
                return jsonify({"status": "success"})
    return jsonify({"message": "Erreur de connexion"}), 401

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json['message']
    reponse = ia_repond(msg, current_user.username)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO messages (user_id, content, role) VALUES (%s, %s, %s)', (current_user.id, msg, 'user'))
            cur.execute('INSERT INTO messages (user_id, content, role) VALUES (%s, %s, %s)', (current_user.id, reponse, 'ia'))
            conn.commit()
    return jsonify({"reponse": reponse})

@app.route('/get_history')
@login_required
def get_history():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT content, role FROM messages WHERE user_id = %s ORDER BY timestamp ASC', (current_user.id,))
            msgs = cur.fetchall()
            return jsonify([dict(m) for m in msgs])

@app.route('/suggest', methods=['POST'])
@login_required
def suggest():
    idea = request.json.get('idea')
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO suggestions (username, idea) VALUES (%s, %s)', (current_user.username, idea))
            conn.commit()
    return jsonify({"status": "success"})

@app.route('/admin_stats')
@login_required
def admin_stats():
    if not current_user.is_admin: return jsonify({"error": "Interdit"}), 403
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT username, is_admin, is_banned FROM users')
            users = cur.fetchall()
            cur.execute('SELECT username, idea FROM suggestions')
            suggs = cur.fetchall()
            return jsonify({"users": [dict(u) for u in users], "suggestions": [dict(s) for s in suggs]})

@app.route('/admin_action', methods=['POST'])
@login_required
def admin_action():
    if not current_user.is_admin: return jsonify({"error": "Interdit"}), 403
    data = request.json
    action, target = data.get('action'), data.get('target')
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if action == 'ban': cur.execute('UPDATE users SET is_banned = 1 WHERE username = %s', (target,))
            elif action == 'unban': cur.execute('UPDATE users SET is_banned = 0 WHERE username = %s', (target,))
            elif action == 'promote': cur.execute('UPDATE users SET is_admin = 1 WHERE username = %s', (target,))
            conn.commit()
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
