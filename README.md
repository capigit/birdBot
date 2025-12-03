**BirdBot — Assistant Ornithologique (UI + MCP + LLM)**

Ce dépôt contient "BirdBot", une application prototype composée de deux services FastAPI :
- une interface web légère (UI) qui sert une page statique et des endpoints LLM (`chatbot_ui.py`),
- un serveur "MCP" (Model Context Protocol) fournissant un modèle spécialiste ResNet-50 pour l'identification d'oiseaux (`mcp_server.py`).

**Description**
- **But**: Fournir une interface conversationnelle permettant de poser des questions générales (via un LLM local — Ollama) et d'identifier des oiseaux à partir d'images en utilisant un modèle ResNet-50 spécialisé. Après identification, la réponse est enrichie par le LLM.
- **Cas d'usage**: reconnaissance d'espèces d'oiseaux (CUB-200 dataset), assistance ornithologique conversationnelle, prototype pour intégration LLM+vision.

**Fonctionnalités principales**
- **Reconnaissance d'images**: endpoint `/predict` exposé par `mcp_server.py` qui renvoie le nom de l'espèce et un message de confiance.
- **Enrichissement LLM**: endpoints `/llm/general` et `/llm/enrich` exposés par `chatbot_ui.py` qui appellent une API Ollama locale pour générer des réponses conversationnelles.
- **UI web**: page statique `static/index.html` + `static/app.js` permettant d'uploader une image ou de poser une question en texte.

**Architecture & Fichiers importants**
- `chatbot_ui.py`: FastAPI app (variable `app`) qui
  - sert les fichiers statiques (dossier `static`) et l'UI,
  - expose `/llm/general` pour questions générales,
  - expose `/llm/enrich` pour enrichir une identification fournie par le MCP en appelant Ollama.
- `mcp_server.py`: FastAPI app (variable `mcp_app`) qui
  - charge `classes.txt` et les poids `resnet50_cub.pth`,
  - expose `/predict` pour recevoir une image et renvoyer l'espèce identifiée (si confiance >= 80%).
- `static/`:
  - `index.html`: UI principale (upload image + formulaire texte),
  - `app.js`: logique côté client — envoie images au MCP et questions au service LLM, gère l'affichage,
  - `styles.css`: styles CSS.
- `classes.txt`: liste des 200 classes (CUB-200) utilisée par le modèle spécialiste.
- `resnet50_cub.pth`: poids pré-entraînés (doit se trouver à la racine) — nécessaire au `mcp_server`.
- `requirements.txt`: dépendances Python requises.

**Entraînement (retrain)**
- Un dossier `EntrainementModel` est disponible et contient les scripts et ressources permettant de réentraîner ou d'ajuster le modèle spécialiste ResNet-50 sur vos données. Consultez ce dossier pour les instructions spécifiques et les dépendances nécessaires au ré-entrainement.

**Technologies utilisées**
- **Langage**: Python
- **Framework web**: FastAPI + Uvicorn
- **Vision**: PyTorch (+ torchvision), PIL (Pillow)
- **Frontend**: HTML/CSS/vanilla JavaScript
- **Templating**: Jinja2 (pour servir `index.html` via FastAPI)
- **LLM**: Ollama `llama3.2:1b`

**Prérequis**
- Python 3.10+ (3.12 recommandé)
- `pip` pour installer les dépendances
- Fichiers suivants présents à la racine du dépôt:
  - `resnet50_cub.pth` (poids du modèle spécialiste)
  - `classes.txt` (liste des classes)
- Service Ollama local (optionnel mais requis pour les réponses LLM) avec le modèle `llama3.2:1b` (ou autre modèle compatible) disponible via `http://localhost:11434/api/generate`.
- Connexions réseau locales autorisées entre les services (CORS déjà configuré pour `mcp_server`).

**Installation**
1. Cloner le dépôt:

```powershell
git clone https://github.com/capigit/birdBot.git
cd birdBot
```

2. Créer un environnement virtuel et l'activer:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

3. Installer les dépendances:

```powershell
pip install -r requirements.txt
```

4. Vérifier que `resnet50_cub.pth` et `classes.txt` sont présents à la racine.

5. (Optionnel) Installer et lancer Ollama si vous voulez les réponses LLM:
- Reportez-vous à la documentation d'Ollama pour l'installation et le chargement de modèles.

**Exécution**
Vous devez lancer les deux services dans deux terminaux distincts (ou les déployer séparément):

- Lancer le MCP (modèle spécialiste):

```powershell
uvicorn mcp_server:mcp_app --port 8001 --reload
```

- Lancer l'UI + endpoints LLM (requiert Ollama pour que l'enrichissement fonctionne):

```powershell
uvicorn chatbot_ui:app --port 8000 --reload
```

Ensuite, ouvrez `http://localhost:8000` dans votre navigateur.

**Commandes utiles / Tests rapides**
- Tester le MCP (curl):

```powershell
curl -F "file=@path\to\bird.jpg" http://127.0.0.1:8001/predict
```

- Tester l'endpoint LLM général (curl):

```powershell
curl -X POST -H "Content-Type: application/json" -d '{"text":"Quel est le comportement hivernal du merle ?"}' http://127.0.0.1:8000/llm/general
```

- Vérifier que Ollama est joignable (exemple basique):

```powershell
curl -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d "{\"model\":\"llama3.2:1b\",\"prompt\":\"Bonjour\"}"
```

**Exemples d'utilisation**
- Dans le navigateur `http://localhost:8000` :
  - Téléversez une photo d'un oiseau via le formulaire "Classifier Image (MCP)". Si la confiance est >= 80% le nom d'espèce sera renvoyé, puis l'UI appellera `/llm/enrich` pour obtenir un court texte informatif.
  - Posez une question en texte dans le champ prévu; elle sera envoyée à `/llm/general` et traitée par Ollama.

**Configuration**
- `chatbot_ui.py` contient deux constantes importantes:
  - `OLLAMA_API_URL` : URL de l'API Ollama (par défaut `http://localhost:11434/api/generate`).
  - `OLLAMA_MODEL` : modèle Ollama utilisé (par défaut `llama3.2:1b`).
- `static/app.js` contient la constante `MCP_URL` pointant vers le MCP (`http://127.0.0.1:8001/predict`).

Pour personnaliser les adresses/ports, modifiez ces constantes ou adaptez le code pour lire des variables d'environnement (ex. `os.getenv`).

**Contribution**
- **Signaler un bug**: ouvrez une issue décrivant le problème et données de reproduction.
- **Proposer une amélioration**: forkez le dépôt, ouvrez une pull request bien ciblée et documentée.
- **Tests**: aucun test automatisé n'est fourni actuellement — contributions pour ajouter une suite de tests sont bienvenues.

**Licence**
- Ce projet est distribué sous la licence **MIT**. Voir le fichier `LICENSE` à la racine du dépôt pour le texte complet.