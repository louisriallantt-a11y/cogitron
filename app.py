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

# --- CONNEXION BLINDÉE ---
def get_db_connection():
    # Suppression de tout ce qui peut gêner dans l'URL
    # Format direct sans fioritures
    db_url = "postgresql://postgres:lvaEThDKHQeeE5pJ@db.avwtqyixixkwcbhbrgcb.supabase.co:5432/postgres"
    return psycopg2.connect(db_url)

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
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # On vérifie/crée la table juste avant au cas où
        cur.execute('CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, color TEXT DEFAULT "#00ff88", is_admin INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0)')
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', 
                    (data['username'], generate_password_hash(data['password'])))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        # Ici on renvoie l'erreur réelle en JSON pour ne plus avoir l'erreur <!DOCTYPE
        return jsonify({"status": "error", "message": str(e)}), 400

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
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "error", "message": "Identifiants faux"}), 401

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.json
        msg = data.get('message')
        # On appelle l'IA
        reponse = ia_repond(msg, current_user.username)
        return jsonify({"reponse": reponse})
    except Exception as e:
        # On force le retour en JSON même si ça plante !
        return jsonify({"reponse": f"Erreur serveur : {str(e)}"}), 200
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
