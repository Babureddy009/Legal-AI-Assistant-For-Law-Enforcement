// Get DOM elements
const messageList = document.getElementById('message-list');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const typingIndicator = document.getElementById('typing-indicator');

// Avatars (FontAwesome icons or emoji)
const userAvatar = '<span class="avatar user-avatar"><i class="fas fa-user"></i></span>';
const botAvatar = '<span class="avatar bot-avatar"><i class="fas fa-robot"></i></span>';

// --- Load previous messages if session_id is present ---
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');

async function loadPreviousMessages() {
    console.log('loadPreviousMessages called');
    console.log('Session ID from URL:', sessionId);
    if (!sessionId) {
        console.log('No sessionId in URL');
        return;
    }
    try {
        const res = await fetch(`/api/chat/history/${sessionId}/messages`);
        if (!res.ok) {
            console.error('Failed to fetch previous messages:', res.status, res.statusText);
            return;
        }
        const messages = await res.json();
        console.log('Loaded previous messages:', messages);
        if (!Array.isArray(messages)) {
            console.error('Expected array of messages, got:', messages);
            return;
        }
        messages.forEach((msg, idx) => {
            console.log(`Rendering message #${idx + 1}:`, msg);
            if (msg.sender === 'user') {
                addUserMessage(msg.content);
                console.log('Called addUserMessage:', msg.content);
            } else if (msg.sender === 'bot') {
                addBotMessage(msg.content);
                console.log('Called addBotMessage:', msg.content);
            } else {
                addSystemMessage(`[${msg.sender}] ${msg.content}`);
                console.log('Called addSystemMessage:', `[${msg.sender}] ${msg.content}`);
            }
        });
        console.log('Message list after rendering previous messages:', messageList.innerHTML);
    } catch (err) {
        console.error('Error loading previous messages:', err);
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    console.log('DOMContentLoaded event fired');
    await loadPreviousMessages();

    // Now create the WebSocket connection, passing session_id if present
    const wsUrl = sessionId ? `ws://localhost:8080/ws?session_id=${sessionId}` : 'ws://localhost:8080/ws';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        addSystemMessage('Connected to chat server');
    };

    ws.onmessage = (event) => {
        hideTyping();
        try {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'user_message':
                    addUserMessage(data.text);
                    break;
                case 'bot_message':
                    if (typeof data.text === 'string' && data.text.trim()) {
                        addBotMessage(data.text.trim());
                    } else if (Array.isArray(data.text)) {
                        data.text.forEach(t => addBotMessage((t || '').trim()));
                    } else {
                        addBotMessage('[Bot error: No text field in response]');
                    }
                    break;
                case 'error':
                    addSystemMessage(data.text);
                    break;
                default:
                    addBotMessage(event.data);
            }
        } catch (e) {
            console.error('Error parsing message:', e);
            addBotMessage(event.data);
        }
    };

    ws.onerror = (error) => {
        addSystemMessage('Connection error occurred');
    };

    ws.onclose = () => {
        addSystemMessage('Connection closed');
    };

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message && ws.readyState === WebSocket.OPEN) {
            addUserMessage(message);
            ws.send(message);
            messageInput.value = '';
            sendButton.disabled = true;
            showTyping();
        }
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

function addSystemMessage(text) {
    const messageElement = document.createElement('li');
    messageElement.className = 'message system-message';
    messageElement.innerHTML = `<span class='system-text'>${text}</span>`;
    messageList.appendChild(messageElement);
    scrollToBottom();
}

function addUserMessage(text) {
    const messageElement = document.createElement('li');
    messageElement.className = 'message sent-message';
    messageElement.innerHTML = `
        <div class='bubble user-bubble'>${escapeAndFormat(text)}</div>
        <span class='avatar user-avatar'><i class="fas fa-user"></i></span>
    `;
    messageList.appendChild(messageElement);
    scrollToBottom();
}

function addBotMessage(text) {
    if (!text || !text.trim()) return; // Prevent empty messages
    const messageElement = document.createElement('li');
    messageElement.className = 'message received-message';
    messageElement.innerHTML = `
        <span class="avatar bot-avatar"><i class="fas fa-robot"></i></span>
        <div class='bubble bot-bubble'>${escapeAndFormat(text)}</div>
    `;
    messageList.appendChild(messageElement);
    scrollToBottom();
}

function addBotMessagesSequentially(messages, idx = 0) {
    if (!messages || idx >= messages.length) return;
    addBotMessage(messages[idx]);
    setTimeout(() => addBotMessagesSequentially(messages, idx + 1), 900 + Math.min(2000, messages[idx].length * 20));
}

function showTyping() {
    typingIndicator.innerHTML = `<span class='typing-dot'></span> Legal AI Assistant is typing...`;
}

function hideTyping() {
    typingIndicator.innerHTML = '';
}

function scrollToBottom() {
    messageList.scrollTop = messageList.scrollHeight;
    messageList.parentElement.scrollTop = messageList.parentElement.scrollHeight;
}

function escapeAndFormat(text) {
    // First escape HTML
    text = text.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;')
               .replace(/"/g, '&quot;')
               .replace(/'/g, '&#039;');

    // Check if this is a legal information response
    if (text.startsWith('Information about')) {
        const sections = text.split('\n\n');
        let formattedText = '';
        
        // Process each section
        for (let section of sections) {
            if (section.startsWith('Information about')) {
                // Extract just the crime name without the prefix
                const crimeName = section.replace('Information about ', '').replace(':', '');
                formattedText += `<h3 class="legal-heading">${crimeName}</h3>`;
            } else if (section.startsWith('Description:')) {
                // Remove the "Description:" prefix
                const description = section.replace('Description:', '').trim();
                formattedText += `<div class="legal-section">
                    <p class="legal-description">${description}</p>
                </div>`;
            } else if (section.startsWith('Severity:')) {
                // Remove the "Severity:" prefix
                const severity = section.replace('Severity:', '').trim();
                formattedText += `<div class="legal-section">
                    <p class="legal-severity">Severity: ${severity}</p>
                </div>`;
            } else if (section.startsWith('Related IPC Sections:')) {
                // Remove the "Related IPC Sections:" prefix
                formattedText += `<div class="legal-section">
                    <h4 class="ipc-heading">IPC Sections</h4>`;
            } else if (section.startsWith('Section')) {
                // Individual IPC section
                const [sectionNum, ...details] = section.split('\n');
                formattedText += `<div class="ipc-section">
                    <h5 class="section-number">${sectionNum}</h5>`;
                
                // Process section details
                for (let detail of details) {
                    if (detail.startsWith('Title:')) {
                        const title = detail.replace('Title:', '').trim();
                        formattedText += `<p class="section-title">${title}</p>`;
                    } else if (detail.startsWith('Punishment:')) {
                        const punishment = detail.replace('Punishment:', '').trim();
                        formattedText += `<p class="punishment">${punishment}</p>`;
                    }
                }
                formattedText += '</div>';
            }
        }
        return formattedText;
    }

    // For other messages, handle basic formatting
    return text.replace(/\n/g, '<br>')
               .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
               .replace(/\*(.*?)\*/g, '<em>$1</em>')
               .replace(/- (.*?)(?:\n|$)/g, '<li>$1</li>');
}

// Event listeners
messageInput.addEventListener('input', () => {
    sendButton.disabled = !messageInput.value.trim();
});

