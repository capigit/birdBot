import torch
from torchvision import models, transforms
from PIL import Image
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# --- FONCTIONS DU MODÈLE SPÉCIALISTE (RESNET-50) ---

def load_classes(filepath="classes.txt"):
    """Charge les noms de classes depuis le fichier classes.txt."""
    try:
        with open(filepath, 'r') as f:
            classes = [line.strip().split('.', 1)[1].strip().replace('_', ' ') for line in f if line.strip() and '.' in line]
        return classes
    except FileNotFoundError:
        print(f"Erreur : Le fichier de classes '{filepath}' est introuvable.")
        return []

def load_specialist_model(model_path="resnet50_cub.pth", num_classes=200):
    """Charge le modèle ResNet-50 et ses poids."""
    model = models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, num_classes)
    
    try:
        # Assure le chargement sur CPU
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        return model
    except FileNotFoundError:
        print(f"Erreur : Le fichier de poids '{model_path}' est introuvable.")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement des poids du modèle : {e}")
        return None

# Transformations d'image standard pour ResNet-50
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def predict_bird(image_file, model, classes):
    """Effectue la prédiction de la classe d'oiseau."""
    try:
        image = Image.open(io.BytesIO(image_file)).convert("RGB")
        image = transform(image).unsqueeze(0)
    except Exception as e:
        return f"Erreur de traitement de l'image : {e}", None

    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        
    max_prob, predicted_index = torch.max(probabilities, 0)
    max_prob = max_prob.item()
    
    # Logique de la règle des 80%
    if max_prob < 0.80:
        message = f"Je suis désolé, je n'ai identifié aucun oiseau avec une confiance suffisante (seulement {max_prob:.2%}). L'image que vous avez soumise n'est probablement pas un oiseau faisant partie des 200 classes d'oiseaux que je peux identifier ou est de trop mauvaise qualité."
        return message, None
    else:
        predicted_class = classes[predicted_index.item()]
        message = f"J'ai identifié l'oiseau comme étant : {predicted_class} avec une confiance de {max_prob:.2%}."
        return message, predicted_class

# --- INITIALISATION DE L'APPLICATION ET DU MODÈLE ---

CLASSES = load_classes("classes.txt")
MODEL = load_specialist_model("resnet50_cub.pth", len(CLASSES)) if CLASSES else None

if MODEL:
    print(f"MCP Server: Modèle spécialiste ResNet-50 chargé pour {len(CLASSES)} classes.")
else:
    print("MCP Server: ATTENTION : Le modèle spécialiste n'a pas pu être chargé. Le point de terminaison MCP échouera.")

mcp_app = FastAPI()

# Configuration CORS pour autoriser les requêtes du ChatBot UI (port 8000)
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000", 
]

mcp_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- POINT DE TERMINAISON MCP ---

@mcp_app.post("/predict")
async def mcp_predict(file: UploadFile = File(...)):
    """Point de terminaison MCP (Model Context Protocol) pour la prédiction d'image."""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Le modèle spécialiste n'est pas chargé ou les classes sont manquantes.")
        
    contents = await file.read()
    message, bird_name = predict_bird(contents, MODEL, CLASSES)
    
    return JSONResponse(content={"message": message, "bird": bird_name})