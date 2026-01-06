import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026'

# --- CONFIG LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

# --- CONNEXION SUPABASE ---
def get_db_connection():
    # ON FORCE L'URL ICI (Pas de crochets, port standard)
    # Si cette URL ne marche pas, c'est que l'ID projet 'avwtqyixixkwcbhbrgcb' est incorrect
    db_url = "postgresql://postgres:lvaEThDKHQeeE5pJ@db.avwtqyixixkwcbhbrgcb.supabase.co:5432/postgres"
    
    # On force le SSL pour Supabase
    return psycopg2.connect(db_url, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                     color TEXT DEFAULT '#00ff88', is_admin INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS messages 
                    (id SERIAL PRIMARY KEY, user_id INTEGER, content TEXT, role TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cur.close()
    conn.close()

# Initialisation silencieuse
try:
    init_db()
except Exception as e:
    print(f"CRASH DB: {e}")

class User(UserMixin):
    def __init__(self, id, username, color, is_admin, is_banned):
        self.id, self.username, self.color, self.is_admin, self.is_banned = id, username, color, is_admin, is_banned

@login_manager.user_loader
def load_user(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                u = cur.fetchone()
                return User(u['id'], u['username'], u['color'], u['is_admin'], u['is_banned']) if u else None
    except: return None

@app.route('/')
def index(): return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    u, p = data.get('username'), data.get('password')
    color = "#00ff88"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO users (username, password, color) VALUES (%s, %s, %s)',
                             (u, generate_password_hash(p), color))
                conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('SELECT * FROM users WHERE username = %s', (data['username'],))
                user = cur.fetchone()
                if user and check_password_hash(user['password'], data['password']):
                    login_user(User(user['id'], user['username'], user['color'], user['is_admin'], user['is_banned']))
                    return jsonify({"status": "success"})
    except: pass
    return jsonify({"status": "error"}), 401

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
