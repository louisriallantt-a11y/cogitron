import os
from groq import Groq

# Récupération de la clé API
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ia_repond(message_utilisateur, nom_utilisateur):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"Tu es Cogitron. Tu parles à {nom_utilisateur}. Sois technique et concis."
            },
            {
                "role": "user",
                "content": message_utilisateur,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content
