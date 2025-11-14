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
        /* GLOBAL */
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 800px; 
            margin: 40px auto; 
            padding: 20px; 
            background-color: #f0f2f5;
        }}
        h1 {{ 
            color: #007bff; 
            text-align: center; 
            margin-bottom: 25px; 
            font-size: 2em;
        }}
        
        /* CHATBOX CONTAINER */
        #chatbox {{ 
            border: none;
            background-color: #ffffff; 
            padding: 15px; 
            height: 400px;
            overflow-y: auto; 
            margin-bottom: 20px; 
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        /* MESSAGE STYLES */
        #chatbox p {{
            padding: 10px;
            margin: 8px 0;
            border-radius: 10px;
            max-width: 80%;
            display: inline-block;
            word-wrap: break-word;
        }}

        .bot {{ 
            background-color: #e6f3ff;
            color: #004d99;
            float: left; 
            text-align: left;
        }}
        .user {{ 
            background-color: #d4edda;
            color: #155724; 
            float: right; 
            text-align: right;
        }}
        
        #chatbox::after {{
            content: "";
            display: table;
            clear: both;
        }}
        
        .user-content {{ 
            display: flex; 
            flex-direction: column; 
            align-items: flex-end; 
        }}
        .user-image {{ 
            max-width: 150px; 
            height: auto; 
            border: 2px solid #28a745;
            margin-top: 5px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        #input-form {{ 
            display: flex; 
            flex-direction: column; 
            gap: 12px; 
            padding: 15px; 
            background-color: #e9ecef; 
            border-radius: 12px; 
            box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
        }}
        input[type="file"] {{
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }}
        button {{ 
            padding: 10px; 
            background-color: #007bff; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 16px; 
            transition: background-color 0.3s;
        }}
        button:hover {{ background-color: #0056b3; }}
        
        #input-form > p {{
            margin: 0;
            padding: 10px;
            background-color: #f8f9fa; 
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <h1>🐦 BirdBot : Assistant Spécialisé</h1>
    <div id="chatbox"></div>
    
    <form id="input-form" onsubmit="event.preventDefault(); handleImageUpload();">
        <p class="bot">
            <strong>BirdBot</strong> : Bonjour ! Je suis BirdBot. 
            Je suis un ChatBot basé sur un petit LLM (conceptuel) et je sers d'interface à mon 
            <strong>Modèle Spécialiste ResNet-50</strong> 
            (disponible via {MCP_URL}). 
            Mon unique fonction est la classification d'images. 
            Pour utiliser le modèle spécialiste via le 
            <strong>Protocole MCP</strong>, veuillez soumettre une image d'oiseau ci-dessous.
        </p>
        <input type="file" id="image-file" accept="image/*" required>
        <button type="submit">Identifier l'oiseau (Appel MCP)</button>
    </form>

    <script>
        const chatbox = document.getElementById('chatbox');
        const fileInput = document.getElementById('image-file');

        function appendMessage(sender, message, imageUrl = null) {{
            const msgContainer = document.createElement('div');
            const pElement = document.createElement('p');
            pElement.className = sender;

            const prefix = document.createElement('span');
            prefix.innerHTML = `<strong>${{sender === 'bot' ? 'BirdBot' : 'Vous'}}</strong> : `;
            pElement.appendChild(prefix);

            const spanText = document.createElement('span');
            spanText.innerHTML = message;  // permet <strong>HTML</strong>
            pElement.appendChild(spanText);

            if (imageUrl) {{
                const imgElement = document.createElement('img');
                imgElement.src = imageUrl;
                imgElement.className = 'user-image';
                
                const imgDiv = document.createElement('div');
                imgDiv.className = 'user-content';
                imgDiv.appendChild(imgElement);

                pElement.appendChild(document.createElement('br'));
                pElement.appendChild(imgDiv);
            }}

            msgContainer.appendChild(pElement);
            chatbox.appendChild(msgContainer);
            chatbox.scrollTop = chatbox.scrollHeight;
        }}

        async function handleImageUpload() {{
            if (fileInput.files.length === 0) {{
                appendMessage('bot', "Veuillez sélectionner un fichier image avant de cliquer sur le bouton.");
                return;
            }}

            const file = fileInput.files[0];

            const reader = new FileReader();
            reader.onload = function(e) {{
                appendMessage('user', `Image soumise : <em>${{file.name}}</em>`, e.target.result);
                proceedWithMCPCall(file);
            }};
            reader.readAsDataURL(file);

            return; 
        }}
        
        async function proceedWithMCPCall(file) {{
            appendMessage('bot', "Requête d'identification reçue. Déclenchement du Modèle Spécialiste (ResNet-50) via le <strong>Protocole MCP</strong>...");
            
            const formData = new FormData();
            formData.append('file', file); 
            
            try {{
                const response = await fetch('{MCP_URL}', {{
                    method: 'POST',
                    body: formData 
                }});
                
                if (!response.ok) {{
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Erreur serveur HTTP ${{response.status}}.`);
                }}

                const data = await response.json();
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
    return HTML_CONTENT