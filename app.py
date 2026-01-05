import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from ia import ia_repond

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-secrete-tres-difficile'

# Configuration de la base de données SQLite
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
init_db()

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('database.db') as conn:
        curr = conn.cursor()
        curr.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        user = curr.fetchone()
        if user:
            return User(user[0], user[1])
    return None

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user.username)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with sqlite3.connect('database.db') as conn:
        curr = conn.cursor()
        curr.execute("SELECT id, username, password FROM users WHERE username = ?", (data['username'],))
        user = curr.fetchone()
        if user and check_password_hash(user[2], data['password']):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Identifiants incorrects"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = generate_password_hash(data['password'])
    try:
        with sqlite3.connect('database.db') as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['username'], hashed_pw))
            return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "Nom d'utilisateur déjà pris"}), 400

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    reponse = ia_repond(data['message'], current_user.username)
    return jsonify({"reponse": reponse})

if __name__ == '__main__':
    app.run(debug=True)
