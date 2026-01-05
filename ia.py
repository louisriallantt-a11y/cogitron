import os
import json
from groq import Groq

# Récupération de la clé API (sécurisée pour le Cloud)
api_key_env = os.environ.get("GROQ_API_KEY")
if not api_key_env:
    # Ta clé par défaut pour ton Mac
    api_key_env = "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"

client = Groq(api_key=api_key_env)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOSSIER_HISTORIQUE = os.path.join(BASE_DIR, "historiques")

def ia_repond(message, id_discussion):
    chemin_complet = os.path.join(DOSSIER_HISTORIQUE, f"{id_discussion}.json")
    os.makedirs(os.path.dirname(chemin_complet), exist_ok=True)
    
    system_prompt = "Tu es COGITRON. Un OS de calcul haute performance. Sois technique, précis et utilise le format Markdown pour tes réponses."

    historique = []
    if os.path.exists(chemin_complet):
        try:
            with open(chemin_complet, "r", encoding="utf-8") as f:
                historique = json.load(f)
        except: historique = []

    historique.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + historique[-10:],
            temperature=0.7
        )
        reponse = completion.choices[0].message.content
        historique.append({"role": "assistant", "content": reponse})
        with open(chemin_complet, "w", encoding="utf-8") as f:
            json.dump(historique, f, ensure_ascii=False, indent=4)
        return reponse
    except Exception as e:
        return f"Erreur système : {str(e)[:50]}"