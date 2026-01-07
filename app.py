from flask import Flask, render_template, send_from_directory, request, jsonify
import os

app = Flask(__name__)

# --- ROUTES POUR L'APPLICATION (PWA) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.getcwd(), 'sw.js')

# --- ROUTE POUR L'IA (Correction erreur 401) ---

@app.route('/chat', methods=['POST'])
def chat():
    # Simulation de réponse (Remplace par ton code Gemini)
    user_data = request.json
    user_message = user_data.get("message", "")
    
    # Si tu as une erreur 401, c'est que ta clé API est mal configurée
    # Assure-toi d'avoir configuré ta clé dans les "Environment Variables" sur Render
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return jsonify({"reply": "Erreur : La clé API n'est pas configurée sur Render ! 🔑"}), 401

    return jsonify({"reply": f"Tu as dit : {user_message}. Je suis prêt ! 😊"})

if __name__ == "__main__":
    app.run(debug=True)
