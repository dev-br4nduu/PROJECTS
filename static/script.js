class JarvisChat {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.resetBtn = document.getElementById('resetBtn');

        this.attachEventListeners();
    }

    attachEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.resetBtn.addEventListener('click', () => this.resetConversation());
    }

    async sendMessage() {
        const message = this.userInput.value.trim();

        if (!message) return;

        this.addUserMessage(message);
        this.userInput.value = '';
        this.userInput.focus();

        if (window.ReadableStream) {
            await this.sendMessageStreaming(message);
        } else {
            await this.sendMessageBlocking(message);
        }
    }

    /** Caminho principal: consome /api/chat/stream via Server-Sent Events. */
    async sendMessageStreaming(message) {
        this.showLoadingIndicator();
        let bubble = null;
        let accumulated = '';

        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            if (!response.ok || !response.body) {
                // Servidor não conseguiu nem abrir o stream — cai pro modo bloqueante.
                this.removeLoadingIndicator();
                return this.sendMessageBlocking(message);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                // Frames SSE são separados por linha em branco dupla.
                let sepIndex;
                while ((sepIndex = buffer.indexOf('\n\n')) !== -1) {
                    const frame = buffer.slice(0, sepIndex);
                    buffer = buffer.slice(sepIndex + 2);
                    const { event, data } = this.parseSSEFrame(frame);
                    if (!event) continue;

                    if (event === 'chunk') {
                        if (!bubble) {
                            this.removeLoadingIndicator();
                            bubble = this.addJarvisMessage('', null, { streaming: true });
                        }
                        accumulated += data.text;
                        this.updateJarvisMessageText(bubble, accumulated);
                    } else if (event === 'error') {
                        this.removeLoadingIndicator();
                        if (bubble) {
                            this.updateJarvisMessageText(bubble, accumulated || `I apologize, sir. ${data.error}`);
                        } else {
                            this.addJarvisMessage(`I apologize, sir. ${data.error}`);
                        }
                        return;
                    } else if (event === 'done') {
                        // Resposta completa: agora sim habilita o feedback 👍/👎.
                        if (bubble) {
                            this.attachFeedbackBar(bubble, { prompt: message, response: accumulated });
                        }
                    }
                }
            }
        } catch (error) {
            this.removeLoadingIndicator();
            if (bubble) {
                this.updateJarvisMessageText(bubble, accumulated || `I apologize, sir. Connection error: ${error.message}`);
            } else {
                this.addJarvisMessage(`I apologize, sir. Connection error: ${error.message}`);
            }
        }
    }

    /** Fallback sem streaming: usado se o navegador não suportar ReadableStream. */
    async sendMessageBlocking(message) {
        this.showLoadingIndicator();
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            this.removeLoadingIndicator();

            if (response.ok) {
                this.addJarvisMessage(data.jarvis, { prompt: message, response: data.jarvis });
            } else {
                this.addJarvisMessage(`I apologize, sir. An error occurred: ${data.error}`);
            }
            this.scrollToBottom();
        } catch (error) {
            this.removeLoadingIndicator();
            this.addJarvisMessage(`I apologize, sir. Connection error: ${error.message}`);
        }
    }

    /** Interpreta um frame SSE ("event: X\ndata: {...}") em {event, data}. */
    parseSSEFrame(frame) {
        let event = null;
        let dataStr = '';
        for (const line of frame.split('\n')) {
            if (line.startsWith('event:')) event = line.slice(6).trim();
            else if (line.startsWith('data:')) dataStr += line.slice(5).trim();
        }
        if (!event) return { event: null, data: null };
        try {
            return { event, data: JSON.parse(dataStr) };
        } catch (e) {
            return { event: null, data: null };
        }
    }

    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<p>${this.escapeHtml(message)}</p>`;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addJarvisMessage(message, feedbackCtx = null, opts = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message jarvis-message';
        messageDiv.innerHTML = `<p>${this.escapeHtml(message)}</p>`;

        // No modo streaming, o texto ainda está chegando: o feedback só é
        // anexado depois, quando a resposta terminar (evento "done").
        if (feedbackCtx && !opts.streaming) {
            this.attachFeedbackBar(messageDiv, feedbackCtx);
        }

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        return messageDiv;
    }

    /** Atualiza o texto de uma bolha de mensagem já criada (usado no streaming). */
    updateJarvisMessageText(messageDiv, text) {
        const p = messageDiv.querySelector('p');
        if (p) p.innerHTML = this.escapeHtml(text);
        this.scrollToBottom();
    }

    /**
     * Anexa a barra de feedback 👍 (rating 5) / 👎 (rating 1) a uma bolha de
     * mensagem. Liga ao loop feedback->retrieval: ensina o JARVIS a priorizar
     * boas respostas e despriorizar ruins em buscas futuras.
     */
    attachFeedbackBar(messageDiv, feedbackCtx) {
        if (messageDiv.querySelector('.feedback-bar')) return; // não duplica

        const fb = document.createElement('div');
        fb.className = 'feedback-bar';
        const up = document.createElement('button');
        up.className = 'feedback-btn';
        up.textContent = '👍';
        up.title = 'Boa resposta';
        const down = document.createElement('button');
        down.className = 'feedback-btn';
        down.textContent = '👎';
        down.title = 'Resposta ruim';

        const send = async (rating, btn) => {
            fb.querySelectorAll('.feedback-btn').forEach(b => b.disabled = true);
            btn.classList.add('feedback-selected');
            try {
                await fetch('/api/feedback/explicit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: feedbackCtx.prompt,
                        response: feedbackCtx.response,
                        rating
                    })
                });
                fb.insertAdjacentHTML('beforeend',
                    '<span class="feedback-thanks">obrigado, senhor</span>');
            } catch (e) {
                fb.querySelectorAll('.feedback-btn').forEach(b => b.disabled = false);
            }
        };
        up.addEventListener('click', () => send(5, up));
        down.addEventListener('click', () => send(1, down));
        fb.appendChild(up);
        fb.appendChild(down);
        messageDiv.appendChild(fb);
    }

    showLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message jarvis-message';
        loadingDiv.id = 'loading-indicator';
        loadingDiv.innerHTML = `
            <div class="loading">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        `;
        this.chatMessages.appendChild(loadingDiv);
        this.scrollToBottom();
    }

    removeLoadingIndicator() {
        const loading = document.getElementById('loading-indicator');
        if (loading) loading.remove();
    }

    async resetConversation() {
        if (confirm('Reset conversation? This will clear all messages.')) {
            try {
                const response = await fetch('/api/reset', {
                    method: 'POST'
                });

                const data = await response.json();

                this.chatMessages.innerHTML = '';
                this.addJarvisMessage(data.greeting);
                this.userInput.focus();
            } catch (error) {
                alert(`Error resetting conversation: ${error.message}`);
            }
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new JarvisChat();
});
