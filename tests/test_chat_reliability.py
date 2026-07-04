"""
Testes de confiabilidade do chat: prompt caching, streaming e tratamento de
erros da API Anthropic.

Cobrem especificamente a regressão encontrada durante o desenvolvimento: o
acesso ao cliente Anthropic (que levanta RuntimeError se faltar a API key)
precisa ficar FORA do try/except que traduz erros de API, senão o RuntimeError
é reembalado como um JarvisAIError genérico (500) em vez de propagar para o
contrato 503 "unconfigured" que a camada Flask e a UI esperam.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import anthropic
import pytest

from jarvis.ai_engine import JarvisAI, JarvisAIError


def _fake_status_error(cls, status: int):
    """Constrói uma exceção real do SDK Anthropic com um httpx.Response válido."""
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(status, request=req, json={"error": {"message": "x"}})
    return cls("x", response=resp, body={"error": {"message": "x"}})


@pytest.fixture()
def ai(tmp_path):
    # __new__ evita inicializar o RAGMemory (não precisamos dele aqui).
    instance = JarvisAI.__new__(JarvisAI)
    instance.use_memory = False
    instance.rag = None
    instance.conversation_history = []
    return instance


# ---- prompt caching ----

def test_system_blocks_cache_the_static_prefix_only(ai):
    blocks = ai._build_system_blocks("qualquer pergunta")
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}
    # Sem memória (rag=None), só existe o bloco estático cacheado.
    assert len(blocks) == 1

def test_conversation_cache_breakpoint_on_second_to_last_turn(ai):
    ai.conversation_history = [
        {"role": "user", "content": "m1"},
        {"role": "assistant", "content": "r1"},
        {"role": "user", "content": "m2"},
        {"role": "assistant", "content": "r2"},
        {"role": "user", "content": "m3"},
    ]
    messages = ai._messages_for_api()
    # Só o penúltimo turno (índice -2) deve carregar o breakpoint de cache.
    for i, msg in enumerate(messages):
        is_cached = bool(
            isinstance(msg["content"], list) and msg["content"][0].get("cache_control")
        )
        assert is_cached == (i == len(messages) - 2), f"turno {i} com cache inesperado"
    # As mensagens não marcadas continuam com content simples (string).
    assert messages[0]["content"] == "m1"
    assert messages[-1]["content"] == "m3"

def test_short_history_has_no_cache_breakpoint(ai):
    ai.conversation_history = [{"role": "user", "content": "oi"}]
    messages = ai._messages_for_api()
    assert messages == ai.conversation_history


# ---- tradução de erros da API ----

@pytest.mark.parametrize("exc,expected_status", [
    (_fake_status_error(anthropic.AuthenticationError, 401), 401),
    (_fake_status_error(anthropic.PermissionDeniedError, 403), 403),
    (_fake_status_error(anthropic.NotFoundError, 404), 404),
    (_fake_status_error(anthropic.RateLimitError, 429), 429),
    (_fake_status_error(anthropic.InternalServerError, 500), 503),
    (_fake_status_error(anthropic.BadRequestError, 400), 400),
])
def test_translate_api_error_maps_to_correct_status(ai, exc, expected_status):
    translated = ai._translate_api_error(exc)
    assert isinstance(translated, JarvisAIError)
    assert translated.status_code == expected_status

def test_translate_connection_and_timeout_errors(ai):
    req = httpx.Request("POST", "https://api.anthropic.com")
    assert ai._translate_api_error(anthropic.APIConnectionError(request=req)).status_code == 502
    assert ai._translate_api_error(anthropic.APITimeoutError(request=req)).status_code == 504


# ---- contrato HTTP: ausência de API key não vira erro genérico ----

@pytest.fixture()
def client_no_key(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.chdir(tmp_path)
    import importlib
    import jarvis.app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()

def test_chat_without_key_is_503_not_500(client_no_key):
    r = client_no_key.post("/api/chat", json={"message": "oi"})
    assert r.status_code == 503
    assert r.get_json()["status"] == "unconfigured"

def test_chat_stream_without_key_reports_unconfigured(client_no_key):
    r = client_no_key.post("/api/chat/stream", json={"message": "oi"})
    assert r.status_code == 200  # SSE: headers já enviados antes do erro
    assert r.content_type.startswith("text/event-stream")
    body = r.get_data(as_text=True)
    assert "event: error" in body
    assert '"status": "unconfigured"' in body
