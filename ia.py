import os
from groq import Groq

# Récupération de la clé dans les variables Render
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ia_repond(message_utilisateur, pseudo):
    if not GROQ_API_KEY:
        return "⚠️ Erreur : Clé API GROQ_API_KEY absente sur Render."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Tu es Cogitron, l'IA futuriste de {pseudo}."},
                {"role": "user", "content": message_utilisateur}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur technique IA : {str(e)}"
