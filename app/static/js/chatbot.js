(function () {
    const DEFAULT_REFUSAL = 'I can only answer questions about CareerIntelli pages: dashboard, resume, career, interview, roadmap, report, and profile.';

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.video-chatbot').forEach(setupChatbot);
    });

    function setupChatbot(widget) {
        const trigger = widget.querySelector('.chatbot-trigger');
        const closeButton = widget.querySelector('.btn-close-chat');
        const panel = widget.querySelector('.chat-panel');
        const suggestions = widget.querySelectorAll('[data-chatbot-suggestion]');
        const input = widget.querySelector('[data-chatbot-input]');
        const sendButton = widget.querySelector('[data-chatbot-send]');
        const messages = widget.querySelector('[data-chatbot-messages]');
        const apiUrl = widget.dataset.chatbotApi || '/api/chatbot/respond';
        const page = widget.dataset.chatbotPage || 'general';

        if (!trigger || !panel || !input || !sendButton || !messages) {
            return;
        }

        ensureVideoPlayback(widget.querySelector('#chatbot-video'));

        trigger.addEventListener('click', () => togglePanel(panel, input));
        if (closeButton) {
            closeButton.addEventListener('click', () => togglePanel(panel, input));
        }

        suggestions.forEach((button) => {
            button.addEventListener('click', () => {
                input.value = button.dataset.chatbotSuggestion || button.textContent.replace(/^✔\s*/, '');
                sendMessage({ widget, panel, input, messages, apiUrl, page, overrideMessage: input.value });
            });
        });

        sendButton.addEventListener('click', () => {
            sendMessage({ widget, panel, input, messages, apiUrl, page });
        });

        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage({ widget, panel, input, messages, apiUrl, page });
            }
        });
    }

    function ensureVideoPlayback(video) {
        if (!video || typeof video.play !== 'function') {
            return;
        }

        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');
        video.playsInline = true;

        const playAttempt = video.play();
        if (playAttempt && typeof playAttempt.catch === 'function') {
            playAttempt.catch(() => {
                video.addEventListener('canplay', () => video.play().catch(() => {}), { once: true });
            });
        }
    }

    function togglePanel(panel, input) {
        panel.classList.toggle('open');
        if (panel.classList.contains('open')) {
            input.focus();
        }
    }

    async function sendMessage({ widget, panel, input, messages, apiUrl, page, overrideMessage = '' }) {
        const message = (overrideMessage || input.value || '').trim();
        if (!message) {
            return;
        }

        appendMessage(messages, message, 'user');
        input.value = '';
        messages.scrollTop = messages.scrollHeight;

        const typingBubble = appendTypingMessage(messages);

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    page,
                }),
            });

            const data = await response.json();
            const reply = data?.reply || DEFAULT_REFUSAL;
            typeMessage(typingBubble, reply);
        } catch (error) {
            console.error('Chatbot error:', error);
            typeMessage(typingBubble, DEFAULT_REFUSAL);
        }

        messages.scrollTop = messages.scrollHeight;
    }

    function appendMessage(messages, text, role) {
        const message = document.createElement('div');
        message.className = `message ${role}`;
        message.textContent = text;
        messages.appendChild(message);
        return message;
    }

    function appendTypingMessage(messages) {
        const message = document.createElement('div');
        message.className = 'message bot';

        const bubble = document.createElement('div');
        bubble.className = 'message-text typing-message';
        message.appendChild(bubble);
        messages.appendChild(message);
        return bubble;
    }

    function typeMessage(element, text) {
        const output = String(text || '').trim() || DEFAULT_REFUSAL;
        let index = 0;
        element.textContent = '';

        const step = () => {
            element.textContent = output.slice(0, index);
            index += 1;
            if (index <= output.length) {
                setTimeout(step, 16);
            }
        };

        step();
    }
})();
