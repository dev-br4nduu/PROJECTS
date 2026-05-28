from anthropic import Anthropic
from jarvis.config import Config

class JarvisAI:
    """Engine de IA do Jarvis utilizando Claude API"""

    def __init__(self):
        self.client = Anthropic()
        self.conversation_history = []
        self.model = "claude-3-5-sonnet-20241022"

    def reset_conversation(self):
        """Limpa o histórico de conversas"""
        self.conversation_history = []

    def process_request(self, user_message: str) -> str:
        """
        Processa uma mensagem do usuário mantendo contexto da conversa.

        Args:
            user_message: Mensagem do usuário

        Returns:
            Resposta do Jarvis
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.MAX_TOKENS,
            system=Config.JARVIS_SYSTEM_PROMPT,
            messages=self.conversation_history,
            temperature=Config.TEMPERATURE
        )

        assistant_message = response.content[0].text

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def get_conversation_history(self) -> list:
        """Retorna o histórico da conversa"""
        return self.conversation_history
