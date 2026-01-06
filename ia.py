import os
from groq import Groq

# Utilise ta clé API directement ici pour être sûr
GROQ_API_KEY = "ta_cle_groq_ici" 

def ia_repond(message_utilisateur, pseudo):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Tu es Cogitron, tu parles à {pseudo}."},
                {"role": "user", "content": message_utilisateur}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        # TRÈS IMPORTANT : On renvoie une chaîne de caractères, pas une erreur
        return f"Erreur IA : {str(e)}"
