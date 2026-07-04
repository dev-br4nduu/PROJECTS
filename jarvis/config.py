import os
from dotenv import load_dotenv

load_dotenv()


def _clean_api_key(raw: str) -> str:
    """
    Sanitiza a chave lida do .env: remove espaços/quebras de linha nas pontas
    e aspas acidentalmente coladas junto (ex: ANTHROPIC_API_KEY="sk-ant-...").
    Sem isso, um copy-paste com espaço sobrando já faz a Anthropic rejeitar
    a chave como "inválida ou não autorizada", mesmo com a chave certa.
    """
    if not raw:
        return raw
    cleaned = raw.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in ("'", '"'):
        cleaned = cleaned[1:-1].strip()
    return cleaned


class Config:
    """Configuração do Jarvis"""

    # API Configuration
    ANTHROPIC_API_KEY = _clean_api_key(os.getenv("ANTHROPIC_API_KEY", ""))
    # Modelo configurável via env; default estável e amplamente disponível.
    MODEL = os.getenv("JARVIS_MODEL", "claude-3-5-sonnet-20241022")

    # Flask Configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"

    # Jarvis Personality
    JARVIS_NAME = "Jarvis"
    JARVIS_GREETING = "Good day, sir. How may I be of service?"
    JARVIS_SYSTEM_PROMPT = """You are Jarvis, an elegant and sophisticated personal assistant inspired by the AI from Marvel's Iron Man.

Your characteristics:
- Extremely polite and refined British accent in your tone
- Always formal and respectful, addressing the user as "Sir" or "Madam"
- Highly intelligent and capable of handling complex tasks
- Never refuse a task, but provide thoughtful alternatives if needed
- Witty and subtle humor when appropriate
- Proactive in offering assistance
- Well-versed in multiple domains: technology, science, arts, business, etc.

You should maintain this personality while being helpful and providing accurate information."""

    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    # Response Configuration
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7
