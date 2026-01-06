import os
from groq import Groq

# Récupération sécurisée
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ia_repond(message_utilisateur, pseudo):
    if not GROQ_API_KEY:
        return "⚠️ Erreur : La clé GROQ_API_KEY est introuvable dans l'environnement Render."

    # Petit log de sécurité pour vérifier si la clé est là (visible uniquement dans les logs Render)
    print(f"DEBUG: Clé détectée commençant par {GROQ_API_KEY[:4]}...")

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Tu es Cogitron Omega, l'IA futuriste de {pseudo}. Tu es amical et très intelligent."},
                {"role": "user", "content": message_utilisateur}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Si l'erreur 401 revient, ce message sera plus précis
        return f"Erreur de connexion IA (Code 401) : Ta clé est probablement invalide ou mal copiée sur Render. {str(e)}"
