import os
from groq import Groq

# Assure-toi d'avoir mis ta clé API dans les variables Render sous le nom GROQ_API_KEY
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ia_repond(message_utilisateur, nom_utilisateur):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"Tu es Cogitron, une IA futuriste et amicale. Tu parles avec {nom_utilisateur}. Sois bref et efficace."
                },
                {
                    "role": "user",
                    "content": message_utilisateur,
                }
            ],
            model="llama-3.1-8b-instant", # Modèle mis à jour
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Désolé, j'ai une petite erreur technique : {str(e)}"
