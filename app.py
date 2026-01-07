import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"reponse": "🚫 Connecte-toi d'abord."}), 401

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         username TEXT UNIQUE, password TEXT, 
                         is_admin INTEGER DEFAULT 0,
                         is_banned INTEGER DEFAULT 0)''')
        conn.commit()
init_db()

class User(UserMixin):
    def __init__(self, id, username, is_admin, is_banned):
        self.id, self.username, self.is_admin, self.is_banned = id, username, is_admin, is_banned

@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        u = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if u: return User(u['id'], u['username'], u['is_admin'], u['is_banned'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        with get_db_connection() as conn:
            # --- SÉCURITÉ ADMIN PERMANENTE ---
            # On vérifie si c'est toi. Si oui, tu es admin d'office.
            if username == "Louis Riallant":
                is_admin = 1
            else:
                # Sinon, on vérifie si la base est vide pour donner l'admin au premier
                count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
                is_admin = 1 if count == 0 else 0
            
            # Insertion dans la base de données
            conn.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                         (username, generate_password_hash(password), is_admin))
            conn.commit()
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Ce pseudo existe déjà"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
        if user and check_password_hash(user['password'], data['password']):
            if user['is_banned']: return jsonify({"status": "error", "message": "Banni"}), 403
            login_user(User(user['id'], user['username'], user['is_admin'], user['is_banned']))
            session['chat_history'] = [] # On vide l'historique à la connexion
            return jsonify({"status": "success", "is_admin": user['is_admin']})
    return jsonify({"status": "error"}), 401

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json.get('message')
    
    # Récupérer l'historique de la session
    history = session.get('chat_history', [])
    history.append({"role": "user", "content": msg})
    
    # Demander à l'IA
    reponse = ia_repond(history, current_user.username)
    
    # Sauvegarder la réponse dans l'historique
    history.append({"role": "assistant", "content": reponse})
    session['chat_history'] = history[-10:] # On garde les 10 derniers messages
    
    return jsonify({"reponse": reponse})

# --- PANEL ADMIN ---
@app.route('/admin_data')
@login_required
def admin_data():
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
    session.pop('chat_history', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
