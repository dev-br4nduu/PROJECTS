from typing import Iterator, List, Dict, Any, Optional

import anthropic
from anthropic import Anthropic

from jarvis.config import Config
from jarvis.learning.rag import RAGMemory


class JarvisAIError(Exception):
    """
    Erro de chat mapeado para um status HTTP apropriado.

    Traduz as exceções específicas do SDK Anthropic (auth, rate limit,
    indisponibilidade, timeout, etc.) em algo que a camada Flask pode repassar
    ao cliente com o código de status correto, em vez de um 500 genérico.
    """

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class JarvisAI:
    """
    Engine de IA do Jarvis utilizando Claude API, com memória RAG real,
    prompt caching e streaming.

    Fluxo por mensagem:
      1. Recupera memórias semanticamente relevantes (preferências + conversas
         passadas) e as anexa como bloco NÃO cacheado após o system prompt
         estático (que é cacheado — ver _build_system_blocks).
      2. Chama o Claude com esse system aumentado, com cache_control marcando
         o prefixo estável da conversa (ver _messages_for_api).
      3. Armazena o novo par (pergunta, resposta) na memória vetorial para
         futuras conversas — é assim que o JARVIS "aprende" com você.
    """

    def __init__(self, use_memory: bool = True, data_dir: str = "jarvis_data"):
        # Cliente criado sob demanda: a app sobe e serve os demais endpoints
        # (RAG, treino, subsistemas) mesmo sem ANTHROPIC_API_KEY configurada.
        self._client = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.model = Config.MODEL
        self.use_memory = use_memory
        self.rag = RAGMemory(data_dir=data_dir) if use_memory else None
        self.last_usage: Dict[str, Any] = {}

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

    # ---------- construção do prompt (cache) ----------

    def _build_system_blocks(self, user_message: str) -> List[Dict[str, Any]]:
        """
        Monta o `system` como blocos de conteúdo, separando o que é ESTÁVEL
        (personalidade do Jarvis — idêntico a cada chamada, portanto cacheável)
        do que é DINÂMICO (memória recuperada para esta query específica, que
        muda a cada mensagem e por isso não deve ser cacheada).

        cache_control só é marcado no bloco estático: é aí que o ganho de
        latência/custo do prompt caching se realiza, já que esse texto se
        repete idêntico em toda chamada.
        """
        blocks: List[Dict[str, Any]] = [{
            "type": "text",
            "text": Config.JARVIS_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }]

        if self.use_memory and self.rag:
            context = self.rag.build_context(user_message, top_k=5)
            if context:
                blocks.append({
                    "type": "text",
                    "text": (
                        "--- Retrieved memory (use it to personalize and stay "
                        f"consistent) ---\n{context}\n--- End retrieved memory ---"
                    ),
                })
        return blocks

    def _messages_for_api(self) -> List[Dict[str, Any]]:
        """
        Retorna o histórico de conversa marcando um breakpoint de cache no
        penúltimo turno. Isso cacheia o prefixo "congelado" da conversa a
        cada novo turno — só a última mensagem (a nova) entra sem cache.
        Requer >=2 mensagens; com menos, retorna o histórico como está.
        """
        history = self.conversation_history
        if len(history) < 2:
            return list(history)

        breakpoint_idx = len(history) - 2
        messages = []
        for i, msg in enumerate(history):
            if i == breakpoint_idx:
                messages.append({
                    "role": msg["role"],
                    "content": [{
                        "type": "text",
                        "text": msg["content"],
                        "cache_control": {"type": "ephemeral"},
                    }],
                })
            else:
                messages.append(msg)
        return messages

    # ---------- tratamento de erros da API ----------

    @staticmethod
    def _translate_api_error(exc: Exception) -> JarvisAIError:
        """Mapeia exceções do SDK Anthropic para um status HTTP significativo."""
        if isinstance(exc, anthropic.AuthenticationError):
            return JarvisAIError("Chave de API inválida ou não autorizada.", 401)
        if isinstance(exc, anthropic.PermissionDeniedError):
            return JarvisAIError("Acesso negado pela API do Claude.", 403)
        if isinstance(exc, anthropic.NotFoundError):
            return JarvisAIError(f"Modelo não encontrado: {exc}", 404)
        if isinstance(exc, anthropic.RateLimitError):
            return JarvisAIError("Limite de requisições da API excedido. Tente novamente em instantes.", 429)
        if isinstance(exc, anthropic.APITimeoutError):
            return JarvisAIError("Tempo esgotado ao falar com a API do Claude.", 504)
        if isinstance(exc, anthropic.APIConnectionError):
            return JarvisAIError("Não foi possível conectar à API do Claude.", 502)
        if isinstance(exc, anthropic.InternalServerError):
            return JarvisAIError("A API do Claude está indisponível no momento.", 503)
        if isinstance(exc, anthropic.BadRequestError):
            return JarvisAIError(f"Requisição inválida: {exc}", 400)
        if isinstance(exc, anthropic.APIStatusError):
            return JarvisAIError(f"Erro da API do Claude: {exc}", 502)
        return JarvisAIError(f"Erro inesperado ao falar com o Claude: {exc}", 500)

    # ---------- chat ----------

    def process_request(self, user_message: str) -> str:
        """Processa uma mensagem, usando e alimentando a memória de longo prazo."""
        self.conversation_history.append({"role": "user", "content": user_message})
        system_blocks = self._build_system_blocks(user_message)
        # Resolve o cliente ANTES do try de tradução de erros da API: se faltar
        # a chave, o RuntimeError deve propagar como está (contrato 503
        # "unconfigured" da camada Flask), não ser reembalado como erro de API.
        client = self.client

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=system_blocks,
                messages=self._messages_for_api(),
                temperature=Config.TEMPERATURE,
            )
        except Exception as exc:
            # A mensagem do usuário já foi anexada ao histórico; remove para
            # não deixar o turno pela metade caso a chamada falhe.
            self.conversation_history.pop()
            raise self._translate_api_error(exc) from exc

        assistant_message = response.content[0].text
        self.last_usage = self._extract_usage(response.usage)

        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        if self.use_memory and self.rag:
            self.rag.remember(user_message, assistant_message)

        return assistant_message

    def process_request_stream(self, user_message: str) -> Iterator[str]:
        """
        Mesmo fluxo de process_request, mas em streaming: produz pedaços de
        texto conforme chegam do Claude. A memória de longo prazo só é
        alimentada ao final, com o texto completo já reunido.
        """
        self.conversation_history.append({"role": "user", "content": user_message})
        system_blocks = self._build_system_blocks(user_message)
        # Mesma razão do process_request: resolve o cliente antes do try que
        # traduz erros de API, para o RuntimeError de chave ausente propagar
        # sem reembalagem.
        client = self.client

        full_text_parts: List[str] = []
        try:
            with client.messages.stream(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=system_blocks,
                messages=self._messages_for_api(),
                temperature=Config.TEMPERATURE,
            ) as stream:
                for text in stream.text_stream:
                    full_text_parts.append(text)
                    yield text
                final_message = stream.get_final_message()
                self.last_usage = self._extract_usage(final_message.usage)
        except Exception as exc:
            self.conversation_history.pop()
            raise self._translate_api_error(exc) from exc

        assistant_message = "".join(full_text_parts)
        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        if self.use_memory and self.rag:
            self.rag.remember(user_message, assistant_message)

    @staticmethod
    def _extract_usage(usage: Any) -> Dict[str, int]:
        """Extrai métricas de uso/cache do response.usage para observabilidade."""
        if usage is None:
            return {}
        return {
            "input_tokens": getattr(usage, "input_tokens", 0) or 0,
            "output_tokens": getattr(usage, "output_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(usage, "cache_creation_input_tokens", 0) or 0,
            "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", 0) or 0,
        }

    def get_conversation_history(self) -> list:
        """Retorna o histórico da sessão atual."""
        return self.conversation_history

    def get_retrieved_context(self, query: str) -> str:
        """Expõe o contexto que seria recuperado para uma query (debug/transparência)."""
        if self.use_memory and self.rag:
            return self.rag.build_context(query, top_k=5)
        return ""
