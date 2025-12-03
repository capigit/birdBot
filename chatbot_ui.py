from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests 
import re 

# --- CONFIGURATION DES SERVICES ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"

app = FastAPI()

# 1. MONTAGE DU DOSSIER STATIQUE
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. TEMPLATING (pour servir l'index.html)

templates = Jinja2Templates(directory="static")


# --- FONCTIONS UTILES ---

def get_llm_response_from_ollama(prompt):
    """Appelle l'API Ollama pour obtenir une réponse conversationnelle."""
    
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 1024 
        }
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=data, timeout=30)
        response.raise_for_status() 
        
        result = response.json()
        
        if 'response' in result:
            return result['response'].strip()
        
        return "Erreur LLM: Réponse non trouvée dans le format Ollama."
        
    except requests.exceptions.ConnectionError:
        return f"Erreur LLM: Connexion refusée. Vérifiez que le service Ollama est lancé et accessible à {OLLAMA_API_URL}."
    except requests.exceptions.RequestException as e:
        return f"Erreur LLM: Problème lors de l'appel de l'API ({e})."

# --- SCHÉMAS D'ENTRÉE ---

class LLMRequest(BaseModel):
    text: str

class LLMEnrichRequest(BaseModel):
    bird_name: str
    original_message: str

# --- POINTS DE TERMINAISON D'API ---

@app.post("/llm/general")
def general_question(request: LLMRequest):
    """
    Point de terminaison pour les questions conversationnelles générales.
    """
    
    prompt = (
        f"Tu es BirdBot, un assistant qui utilise Llama 3.2 (1B). Réponds à la question suivante: '{request.text}'. "
        f"Si la question concerne les oiseaux, réponds en tant qu'expert ornithologue. Si elle concerne ton identité, dis que tu es BirdBot. Sois bref. "
    )
    
    llm_response = get_llm_response_from_ollama(prompt)
    
    return {"response": llm_response}


@app.post("/llm/enrich")
def enrich_response(request: LLMEnrichRequest):
    """
    Point de terminaison appelé par le JavaScript après la classification réussie (pour enrichissement).
    """
    
    prompt = (
        f"Tu es BirdBot, un expert en ornithologie. Le modèle de vision ResNet-50 a identifié l'oiseau comme étant : '{request.bird_name}'. "
        f"En utilisant cette information, réponds de manière conversationnelle et engageante en ajoutant un fait intéressant sur cet oiseau. "
        f"Commence ta réponse par une confirmation de l'identification: {request.original_message}. Ne dépasse pas 3 phrases. "
    )
    
    llm_response = get_llm_response_from_ollama(prompt)
    
    if llm_response.startswith("Erreur LLM"):
        return {"response": llm_response, "bird": request.bird_name}
    
    return {"response": llm_response, "bird": request.bird_name}

# --- ROUTE PRINCIPALE ---

@app.get("/", response_class=HTMLResponse)
async def serve_chatbot_ui(request: Request):
    """Route principale pour l'interface utilisateur."""
    return templates.TemplateResponse("index.html", {"request": request})