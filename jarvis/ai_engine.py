from anthropic import Anthropic
from jarvis.config import Config
from jarvis.learning.rag import RAGMemory


class JarvisAI:
    """
    Engine de IA do Jarvis utilizando Claude API, agora com memória RAG real.

    Fluxo por mensagem:
      1. Recupera memórias semanticamente relevantes (preferências + conversas
         passadas) e injeta no system prompt.
      2. Chama o Claude com esse prompt aumentado.
      3. Armazena o novo par (pergunta, resposta) na memória vetorial para
         futuras conversas — é assim que o JARVIS "aprende" com você.
    """

    def __init__(self, use_memory: bool = True, data_dir: str = "jarvis_data"):
        # Cliente criado sob demanda: a app sobe e serve os demais endpoints
        # (RAG, treino, subsistemas) mesmo sem ANTHROPIC_API_KEY configurada.
        self._client = None
        self.conversation_history = []
        self.model = Config.MODEL
        self.use_memory = use_memory
        self.rag = RAGMemory(data_dir=data_dir) if use_memory else None

    @property
    def client(self) -> Anthropic:
        """Instancia o cliente Anthropic sob demanda, com erro claro se faltar a chave."""
        if self._client is None:
            if not Config.ANTHROPIC_API_KEY:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY não configurada. Defina-a no arquivo .env "
                    "(veja .env.example) para usar o chat com o Claude."
                )
            self._client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        return self._client

    def reset_conversation(self):
        """Limpa o histórico da sessão (a memória de longo prazo persiste)."""
        self.conversation_history = []

    def process_request(self, user_message: str) -> str:
        """Processa uma mensagem, usando e alimentando a memória de longo prazo."""
        self.conversation_history.append({"role": "user", "content": user_message})

        # 1. System prompt aumentado com memória recuperada
        system_prompt = Config.JARVIS_SYSTEM_PROMPT
        if self.use_memory and self.rag:
            system_prompt = self.rag.augmented_system_prompt(
                Config.JARVIS_SYSTEM_PROMPT, user_message, top_k=5
            )

        # 2. Chamada ao Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.MAX_TOKENS,
            system=system_prompt,
            messages=self.conversation_history,
            temperature=Config.TEMPERATURE,
        )
        assistant_message = response.content[0].text

        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        # 3. Armazena a troca na memória de longo prazo
        if self.use_memory and self.rag:
            self.rag.remember(user_message, assistant_message)

        return assistant_message

    def get_conversation_history(self) -> list:
        """Retorna o histórico da sessão atual."""
        return self.conversation_history

    def get_retrieved_context(self, query: str) -> str:
        """Expõe o contexto que seria recuperado para uma query (debug/transparência)."""
        if self.use_memory and self.rag:
            return self.rag.build_context(query, top_k=5)
        return ""
