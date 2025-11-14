from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# L'URL où le serveur MCP doit tourner (Port 8001)
MCP_URL = "http://127.0.0.1:8001/predict"

app = FastAPI()

# --- INTERFACE CHATBOT UI (HTML/JavaScript) ---

HTML_CONTENT = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BirdBot - ChatBot UI</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; background-color: #f4f4f4; }}
        h1 {{ color: #007bff; text-align: center; }}
        #chatbox {{ border: 1px solid #ccc; background-color: white; padding: 15px; height: 350px; overflow-y: scroll; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .bot {{ color: #007bff; text-align: left; padding: 5px 0; border-bottom: 1px dotted #eee; }}
        .user {{ color: #28a745; text-align: right; padding: 5px 0; border-bottom: 1px dotted #eee; }}
        .user-content {{ display: flex; flex-direction: column; align-items: flex-end; }}
        .user-image {{ max-width: 150px; height: auto; border: 1px solid #ccc; margin-top: 5px; border-radius: 4px; }}
        #input-form {{ display: flex; flex-direction: column; gap: 10px; padding: 10px; background-color: #e9ecef; border-radius: 8px; }}
        button {{ padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background-color: #0056b3; }}
    </style>
</head>
<body>
    <h1>🐦 BirdBot : Assistant Spécialisé</h1>
    <div id="chatbox"></div>
    
    <form id="input-form" onsubmit="event.preventDefault(); handleImageUpload();">
        <p class="bot">**BirdBot** : Bonjour ! Je suis BirdBot. Je suis un ChatBot basé sur un petit LLM (conceptuel) et je sers d'interface à mon **Modèle Spécialiste ResNet-50** (disponible via {MCP_URL}). Mon unique fonction est la classification d'images. Pour utiliser le modèle spécialiste via le **Protocole MCP**, veuillez soumettre une image d'oiseau ci-dessous.</p>
        <input type="file" id="image-file" accept="image/*" required>
        <button type="submit">Identifier l'oiseau (Appel MCP)</button>
    </form>

    <script>
        const chatbox = document.getElementById('chatbox');
        const fileInput = document.getElementById('image-file');

        function appendMessage(sender, message, imageUrl = null) {{
            const msgElement = document.createElement('p');
            msgElement.className = sender;
            
            // Crée un conteneur pour le message (pour aligner l'image et le texte)
            const contentDiv = document.createElement('div');
            contentDiv.className = 'user-content';
            
            // Ajoute le préfixe du locuteur
            const prefix = document.createElement('span');
            prefix.innerHTML = `**${{sender === 'bot' ? 'BirdBot' : 'Vous'}}** : `;
            contentDiv.appendChild(prefix);

            // Ajoute le message textuel
            const textNode = document.createTextNode(message);
            contentDiv.appendChild(textNode);

            // Si une URL d'image est fournie, crée et ajoute l'élément <img>
            if (imageUrl) {{
                const imgElement = document.createElement('img');
                imgElement.src = imageUrl;
                imgElement.className = 'user-image';
                contentDiv.appendChild(imgElement);
            }}

            msgElement.appendChild(contentDiv);
            chatbox.appendChild(msgElement);
            chatbox.scrollTop = chatbox.scrollHeight;
        }}

        async function handleImageUpload() {{
            if (fileInput.files.length === 0) {{
                appendMessage('bot', "Veuillez sélectionner un fichier image avant de cliquer sur le bouton.");
                return;
            }}

            const file = fileInput.files[0];

            // 1. Affiche l'image dans le chatbox AVANT l'envoi
            const reader = new FileReader();
            reader.onload = function(e) {{
                // Affiche l'image soumise par l'utilisateur
                appendMessage('user', `Image soumise : *${{file.name}}*`, e.target.result);
                
                // Continue le processus d'envoi après l'affichage
                proceedWithMCPCall(file);
            }};
            reader.readAsDataURL(file); // Lit le fichier comme une URL de données

            // Empêche la fonction de se terminer immédiatement
            return; 
        }}
        
        async function proceedWithMCPCall(file) {{
            appendMessage('bot', "Requête d'identification reçue. Déclenchement du Modèle Spécialiste (ResNet-50) via le **Protocole MCP**...");
            
            const formData = new FormData();
            formData.append('file', file); 
            
            try {{
                // L'interface appelle l'URL du serveur MCP externe
                const response = await fetch('{MCP_URL}', {{
                    method: 'POST',
                    body: formData 
                }});
                
                if (!response.ok) {{
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Erreur serveur HTTP ${{response.status}}.`);
                }}

                const data = await response.json();

                // Affichage de la réponse du MCP
                appendMessage('bot', data.message);
                
            }} catch (error) {{
                console.error('Erreur lors de l\\'identification :', error);
                appendMessage('bot', 'Une erreur critique est survenue : ' + error.message + '. Vérifiez que le serveur MCP est bien lancé sur le port 8001.');
            }}
            
            fileInput.value = '';
        }}

    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_chatbot_ui():
    """Route principale pour l'interface utilisateur."""
    return HTML_CONTENT