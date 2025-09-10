const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');

// --- Handle form submission ---
chatForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevents the page from reloading
    const userMessage = messageInput.value.trim();

    if (userMessage) {
        // Display the user's message
        addMessage(userMessage, 'user');
        // Send the message to the API and get a response
        sendMessageToAPI(userMessage);
        // Clear the input box
        messageInput.value = '';
    }
});

// --- Function to add a message to the chat window ---
function addMessage(text, sender, imageUrl = null) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);

    const textElement = document.createElement('p');
    textElement.innerText = text;
    messageElement.appendChild(textElement);

    // If there's an image URL, create and add the image element
    if (imageUrl) {
        const imageElement = document.createElement('img');
        imageElement.src = imageUrl;
        messageElement.appendChild(imageElement);
    }
    
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll to the bottom
}

// --- Function to send a message to the FastAPI backend ---
async function sendMessageToAPI(message) {
    try {
        const response = await fetch('http://127.0.0.1:8000/find-meme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: message }),
        });

        const data = await response.json();
        const botResponse = data.response;

        // The image path will be '/static/' + the filename from the API
        const imageUrl = `/static/${botResponse.filename}`;
        
        // Display the bot's text answer and the image
        addMessage(botResponse.answer, 'bot', imageUrl);

    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, something went wrong. Please try again.', 'bot');
    }
}