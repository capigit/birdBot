// --- Configuration ---
const MCP_URL = "http://127.0.0.1:8001/predict"; // URL fixe du MCP
const GENERAL_API_URL = '/llm/general'; // Endpoint pour questions générales
const ENRICH_API_URL = '/llm/enrich'; // Endpoint pour enrichissement après MCP

// --- Éléments DOM ---
const chatbox = document.getElementById('chatbox');
const fileInput = document.getElementById('image-file');
const textInput = document.getElementById('text-input');

// FONCTION UTILITAIRE pour convertir le Markdown
function formatMessage(message) {
    let formatted = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

// FONCTION UTILITAIRE pour afficher un message dans le chatbox
function appendMessage(sender, message, imageUrl = null) {
    const msgContainer = document.createElement('div');
    msgContainer.className = sender;
    
    const pElement = document.createElement('p');
    const formattedMessage = formatMessage(message);
    pElement.innerHTML = formattedMessage; 
    
    if (imageUrl) {
        const imgElement = document.createElement('img');
        imgElement.src = imageUrl;
        imgElement.className = 'user-image';
        
        const imgDiv = document.createElement('div');
        imgDiv.className = 'user-content';
        imgDiv.appendChild(imgElement);

        pElement.appendChild(document.createElement('br'));
        pElement.appendChild(imgDiv);
    }

    msgContainer.appendChild(pElement);
    chatbox.appendChild(msgContainer);
    chatbox.scrollTop = chatbox.scrollHeight;
}

// NOUVELLE FONCTION: Gère l'envoi de texte
async function handleTextSubmit() {
    const text = textInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    textInput.value = '';

    appendMessage('bot', "**BirdBot** : Je consulte mon cerveau (Llama 3.2:1B) pour vous répondre...");

    try {
        // Envoi à la nouvelle API /llm/general
        const response = await fetch(GENERAL_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erreur serveur HTTP ${response.status}.`);
        }

        const data = await response.json();
        
        // Affiche la réponse de Llama
        appendMessage('bot', "**BirdBot** : " + data.response);

    } catch (error) {
        console.error('Erreur lors de la question générale :', error);
        let errorMessage = error.message.includes('Failed to fetch') ? "Erreur de communication avec le serveur FastAPI. Vérifiez votre console." : error.message;
        appendMessage('bot', "Une erreur critique est survenue : " + errorMessage);
    }
}

// FONCTION IMAGE
async function handleImageUpload() {
    if (fileInput.files.length === 0) {
        appendMessage('bot', "Veuillez sélectionner un fichier image avant de cliquer sur le bouton.");
        return;
    }

    const file = fileInput.files[0];
    
    const fileUrl = URL.createObjectURL(file);
    appendMessage('user', `Image soumise : *${file.name}*`, fileUrl);
    
    await proceedWithMCPCall(file);
    
    URL.revokeObjectURL(fileUrl);
}

async function proceedWithMCPCall(file) {
    appendMessage('bot', "**BirdBot** : Requête d'identification reçue. Déclenchement du Modèle Spécialiste (ResNet-50) via le **Protocole MCP**...");
    
    const formData = new FormData();
    formData.append('file', file); 
    
    try {
        const response = await fetch(MCP_URL, {
            method: 'POST',
            body: formData 
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erreur serveur HTTP ${response.status}.`);
        }

        const data = await response.json();
        
        let finalMessage = data.message;
        
        if (data.bird) {
            appendMessage('bot', "**BirdBot** : Identification réussie! J'utilise maintenant Llama 3.2 (1B) pour vous fournir des informations...");

            const llm_response = await fetch(ENRICH_API_URL, {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({ bird_name: data.bird, original_message: data.message })
            });
            
            const llm_data = await llm_response.json();

            if (llm_response.ok) {
                finalMessage = llm_data.response;
            } else {
                finalMessage = "Erreur LLM: " + llm_data.response;
            }
        }
        
        appendMessage('bot', finalMessage);
        
    } catch (error) {
        console.error("Erreur lors de l'identification :", error);
        
        let errorMessage = error.message;
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('refused')) {
            errorMessage = "Erreur de communication. Le serveur MCP n'a pas pu être contacté. **Vérifiez que le serveur MCP est bien lancé sur le port 8001.**";
        }
        appendMessage('bot', "Une erreur critique est survenue : " + errorMessage);
    }
    
    fileInput.value = '';
}

// Attach handlers to forms (in case inline onsubmit removed)
const imageForm = document.getElementById('image-form');
const textForm = document.getElementById('text-form');
if (imageForm) imageForm.onsubmit = (e) => { e.preventDefault(); handleImageUpload(); };
if (textForm) textForm.onsubmit = (e) => { e.preventDefault(); handleTextSubmit(); };
