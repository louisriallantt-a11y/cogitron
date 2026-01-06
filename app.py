import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

def get_db_connection():
    url_directe = "postgresql://postgres:lvaEThDKHQeeE5pJ@db.avwtqyixixkwcbhbrgcb.supabase.co:5432/postgres"
    db_url = os.environ.get('DATABASE_URL', url_directe)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(db_url)

class User(UserMixin):
    def __init__(self, id, username, color, is_admin, is_banned):
        self.id, self.username, self.color, self.is_admin, self.is_banned = id, username, color, is_admin, is_banned

@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            u = cur.fetchone()
            return User(u['id'], u['username'], u['color'], u['is_admin'], u['is_banned']) if u else None

@app.route('/')
def index(): return render_template('index.html')

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
            except: return jsonify({"message": "Erreur"}), 400

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
    return jsonify({"message": "Erreur"}), 401

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
            return jsonify({"users": users, "suggestions": suggs})

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

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json['message']
    reponse = ia_repond(msg, current_user.username)
    return jsonify({"reponse": reponse})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
