
-----

# 🐦 BirdBot : Assistant de Classification d'Oiseaux

Ce projet met en œuvre un ChatBot léger (**BirdBot** - `chatbot_ui.py`) servant d'interface utilisateur à un modèle de *machine learning* spécialisé (ResNet-50) via un **Model Context Protocol (MCP)** implémenté avec FastAPI.

Le modèle spécialiste est entraîné sur le jeu de données **Caltech-UCSD Birds 200 (CUB-200)** et est capable de classer 200 espèces d'oiseaux.

## 📁 Structure du Projet

```
.
├── chatbot_ui.py       # L'interface utilisateur du ChatBot (FastAPI sur port 8000)
├── mcp_server.py       # Le serveur MCP/Modèle Spécialiste (FastAPI sur port 8001)
├── classes.txt         # Fichier contenant les 200 noms de classes d'oiseaux
└── resnet50_cub.pth    # Poids entraînés du modèle ResNet-50
```

## ⚙️ 1. Installation

### 1.1. Prérequis

Assurez-vous d'avoir **Python 3.8+** et **pip** installés.

### 1.2. Création de l'environnement virtuel

Il est fortement recommandé d'utiliser un environnement virtuel :

```bash
python -m venv venv
# Activer l'environnement (Windows)
.\venv\Scripts\activate
# Activer l'environnement (Linux/macOS)
# source venv/bin/activate
```

### 1.3. Installation des dépendances

Ce projet nécessite `torch`, `torchvision` (pour ResNet-50) et `fastapi`/`uvicorn` (pour les serveurs).

```bash
pip install torch torchvision numpy Pillow fastapi uvicorn python-multipart
```

## 🚀 2. Démarrage du Système

### Étape 2.1. Lancer le Serveur MCP (Terminal 1)

Le serveur MCP (`mcp_server.py`) charge le modèle ResNet-50 et écoute les requêtes de prédiction sur le **Port 8001**.

```bash
# Assurez-vous d'être dans l'environnement virtuel et dans le répertoire du projet
(venv) uvicorn mcp_server:mcp_app --port 8001 --reload
```

Vous devriez voir le message : `MCP Server: Modèle spécialiste ResNet-50 chargé pour 200 classes.`

-----

### Étape 2.2. Lancer le ChatBot UI (Terminal 2)

Le ChatBot UI (`chatbot_ui.py`) sert l'interface utilisateur et envoie les requêtes au serveur MCP sur le port 8001. Il écoute sur le **Port 8000**.

```bash
# Assurez-vous d'être dans l'environnement virtuel et dans le répertoire du projet
(venv) uvicorn chatbot_ui:app --port 8000 --reload
```

Vous devriez voir le message : `INFO: Uvicorn running on http://127.0.0.1:8000`

-----

## 💻 3. Mode d'Emploi

1.  **Accédez** au ChatBot UI dans votre navigateur :
    $$\rightarrow \quad \text{[http://127.0.0.1:8000](http://127.0.0.1:8000)}$$
2.  Lisez le message de bienvenue de **BirdBot**.
3.  **Soumettez** une image d'oiseau via l'interface d'upload. L'image apparaîtra dans la conversation.
4.  Cliquez sur **"Identifier l'oiseau (Appel MCP)"**.

### Comportement du Système

  * **Si la confiance est $\geq 50\%$ :** Le BirdBot renvoie l'espèce identifiée et le pourcentage de confiance.
  * **Si la confiance est $< 50\%$ :** Le BirdBot renvoie le message de sécurité indiquant que l'image n'est probablement pas un oiseau.

-----

Veuillez mettre à jour votre fichier `chatbot_ui.py` et, si vous le souhaitez, votre `mcp_server.py` pour refléter le nom **BirdBot** dans les messages de log du terminal. Après cela, nous pourrons passer à d'autres améliorations ou à la documentation.