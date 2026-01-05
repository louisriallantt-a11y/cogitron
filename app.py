from flask import Flask, render_template, request, jsonify, session
import ia
import os

app = Flask(__name__)
app.secret_key = "cogitron_secret_key_2026"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", "").lower().strip()
    if not username: return jsonify({"status": "error"}), 400
    session['user'] = username
    return jsonify({"status": "ok"})

@app.route('/get_discussions')
def get_discs():
    user = session.get('user')
    if not user: return jsonify({"discussions": []})
    user_path = os.path.join(ia.DOSSIER_HISTORIQUE, user)
    if not os.path.exists(user_path): return jsonify({"discussions": []})
    return jsonify({"discussions": [f for f in os.listdir(user_path) if f.endswith('.json')]})

@app.route('/chat', methods=['POST'])
def chat():
    user = session.get('user', 'invite')
    data = request.json
    # Cogitron répond directement
    reponse = ia.ia_repond(data.get("message"), f"{user}/{data.get('id_discussion')}")
    return jsonify({"reponse": reponse})

if __name__ == '__main__':
    app.run(debug=True, port=5000)