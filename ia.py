import os
from groq import Groq

# Remplace par ta vraie clé API Groq
# Tu peux aussi mettre os.environ.get('GROQ_API_KEY') si tu l'as configurée sur Render
GROQ_API_KEY = "ta_cle_api_ici" 

client = Groq(api_key=GROQ_API_KEY)

def ia_repond(message_utilisateur, pseudo):
    try:
        # Prompt système pour donner une personnalité à ton IA
        system_prompt = f"Tu es Cogitron Omega, une IA futuriste. Tu parles à {pseudo}."
        
        completion = client.chat.completions.create(
            # On utilise le modèle le plus stable (Llama 3.1 8b)
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_utilisateur}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return completion.choices[0].message.content

    except Exception as e:
        print(f"Erreur IA : {e}")
        return "Désolé, mon cerveau de silicium surchauffe... (Erreur de connexion avec l'IA)"
