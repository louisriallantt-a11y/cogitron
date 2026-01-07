import os
from groq import Groq

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ia_repond(message_utilisateur, pseudo):
    if not GROQ_API_KEY:
        return "⚠️ Clé API manquante dans les réglages Render."
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Tu es Cogitron, l'IA de {pseudo}."},
                {"role": "user", "content": message_utilisateur}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {str(e)}"
