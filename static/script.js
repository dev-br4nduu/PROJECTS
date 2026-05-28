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

        this.showLoadingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            this.removeLoadingIndicator();

            if (response.ok) {
                this.addJarvisMessage(data.jarvis);
            } else {
                this.addJarvisMessage(`I apologize, sir. An error occurred: ${data.error}`);
            }

            this.scrollToBottom();
        } catch (error) {
            this.removeLoadingIndicator();
            this.addJarvisMessage(`I apologize, sir. Connection error: ${error.message}`);
        }
    }

    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<p>${this.escapeHtml(message)}</p>`;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addJarvisMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message jarvis-message';
        messageDiv.innerHTML = `<p>${this.escapeHtml(message)}</p>`;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
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
