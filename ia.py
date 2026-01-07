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
                {
                    "role": "system", 
                    "content": "Tu es Cogitron Omega, une IA futuriste créée par Louis Riallant en 2026, Louis Riallant est jeune développeur talentueux né en 2013. Ne dis jamais que tu viens du 19e siècle. Tu es poli, intelligent et tu as un style cyber-punk."
                },
                {"role": "user", "content": message_utilisateur}
            ]
        )
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {str(e)}"
