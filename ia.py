import os
from groq import Groq

# Récupération sécurisée de la clé
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ia_repond(message_utilisateur, pseudo):
    if not GROQ_API_KEY:
        return "⚠️ Erreur : Configure la variable GROQ_API_KEY sur Render."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        # Prompt corrigé pour éviter les hallucinations sur ton nom
        system_prompt = f"Tu es Cogitron Omega, une IA avancée. Tu discutes avec {pseudo}. Sois amical, intelligent et n'invente pas de fausse biographie historique."
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_utilisateur}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Désolé Louis, j'ai un bug moteur : {str(e)}"
