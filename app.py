import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Vérification si le dossier templates existe au démarrage
@app.before_first_request
def check_files():
    if not os.path.exists('templates/index.html'):
        print("⚠️ ALERTE : Le fichier templates/index.html est INTROUVABLE !")

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        # Si le fichier manque, on affiche l'erreur au lieu d'une page blanche
        return f"Erreur critique : Le fichier index.html est introuvable dans le dossier templates. ({str(e)})", 500

# Garde tes autres routes (login, register, chat) ici...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
