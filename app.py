import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-ultra-secret-2026'

# --- GESTION DE LA BASE DE DONNÉES ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         username TEXT UNIQUE NOT NULL, 
                         password TEXT NOT NULL)''')
        conn.commit()
init_db()

# --- GESTION DES SESSIONS UTILISATEURS ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index' # Redirige vers l'accueil si non connecté

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return User(user['id'], user['username'])
    return None

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    u, p = data.get('username'), data.get('password')
    if not u or not p: return jsonify({"message": "Champs vides"}), 400
    
    hashed_pw = generate_password_hash(p)
    try:
        with get_db_connection() as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (u, hashed_pw))
            conn.commit()
        return jsonify({"status": "success"})
    except sqlite3.IntegrityError:
        return jsonify({"message": "Ce nom d'utilisateur existe déjà"}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        u, p = data.get('username'), data.get('password')
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (u,)).fetchone()
            if user and check_password_hash(user['password'], p):
                login_user(User(user['id'], user['username']))
                return jsonify({"status": "success"})
        return jsonify({"message": "Identifiants incorrects"}), 401
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    # On passe le message ET le nom de l'utilisateur à l'IA
    reponse = ia_repond(data['message'], current_user.username)
    return jsonify({"reponse": reponse})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
