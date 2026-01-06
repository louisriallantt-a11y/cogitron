import os
from groq import Groq

# os.environ.get va chercher la clé que tu as cachée dans Render
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ia_repond(message_utilisateur, pseudo):
    if not GROQ_API_KEY:
        return "Erreur : La clé API n'est pas configurée dans les paramètres Render."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Tu es Cogitron Omega, une IA futuriste. Tu parles à {pseudo}."},
                {"role": "user", "content": message_utilisateur}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Désolé, j'ai rencontré une erreur technique : {str(e)}"
