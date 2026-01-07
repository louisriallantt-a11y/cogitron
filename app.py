import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cogitron-omega-2026'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

login_manager = LoginManager()
login_manager.init_app(app)

# FORCE LE JSON MEME EN CAS D'ERREUR SUR LE SERVEUR
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Le serveur a crashé, regarde les logs Render"}), 500

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

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    reponse = ia_repond(data.get('message'), current_user.username)
    return jsonify({"reponse": reponse})

# ... (garde tes autres routes register/login identiques au message précédent)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
