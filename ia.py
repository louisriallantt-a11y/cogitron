import os
from groq import Groq

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ia_repond(historique_messages, pseudo):
    if not GROQ_API_KEY:
        return "⚠️ Erreur : Clé API manquante."
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # On définit la personnalité
        system_prompt = {
            "role": "system", 
            "content": f"Tu es Cogitron Omega, l'IA futuriste de {pseudo}. Tu as été créé par Louis Riallant en 2026. Tu es brillant, sarcastique mais amical. Tu te souviens de la discussion."
        }
        
        # On assemble le prompt système + l'historique
        messages_complets = [system_prompt] + historique_messages

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages_complets,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {str(e)}"
