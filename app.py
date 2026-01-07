import os
from flask import Flask, render_template, send_from_directory, request, jsonify

app = Flask(__name__)

# Routes pour les fichiers de l'App (PWA)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    # Remplace ici par ton intégration Gemini plus tard
    return jsonify({"reply": f"Salut papa ! J'ai bien reçu : {user_message} 😊"})

if __name__ == "__main__":
    # C'EST CETTE LIGNE QUI CHANGE TOUT POUR RENDER :
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
