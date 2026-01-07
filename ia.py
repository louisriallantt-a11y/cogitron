import os
from groq import Groq

# On récupère la clé cachée dans Render
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ia_repond(message_utilisateur, pseudo):
    # Vérification si la clé existe
    if not GROQ_API_KEY:
        return "⚠️ Erreur : Je ne trouve pas ma clé API dans les réglages Render."

    try:
        # Initialisation du client Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        # Envoi de la requête à l'IA
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Tu es Cogitron, l'IA futuriste de {pseudo}. Sois amical et brillant."},
                {"role": "user", "content": message_utilisateur}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Désolé, j'ai un petit souci technique : {str(e)}"
