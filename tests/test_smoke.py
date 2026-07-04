"""
Testes de fumaça — cobrem o NÚCLEO real e testado do JARVIS.

Foco: garantir que a aplicação sobe e que o aprendizado real (RAG, feedback,
treino) funciona. Não testa os subsistemas conceituais (que são simulados).

Rodar:
    pip install pytest
    pytest tests/ -q
"""

import os
import sys
import tempfile

# Torna o pacote jarvis importável.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


@pytest.fixture()
def client(monkeypatch, tmp_path):
    # Isola os dados de cada teste num diretório temporário.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")  # sem chave: testa resiliência
    monkeypatch.chdir(tmp_path)
    # Import tardio para pegar o cwd temporário.
    import importlib
    import jarvis.app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_app_boots_and_serves_ui(client):
    r = client.get("/")
    assert r.status_code == 200

def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "healthy"

def test_chat_without_key_returns_503(client):
    r = client.post("/api/chat", json={"message": "oi"})
    assert r.status_code == 503
    assert r.get_json()["status"] == "unconfigured"

def test_system_status_works_without_key(client):
    assert client.get("/api/system/status").status_code == 200


# ---- Aprendizado real (sem depender da API do Claude) ----

def test_vector_memory_semantic_search(tmp_path):
    from jarvis.learning.rag import RAGMemory
    rag = RAGMemory(data_dir=str(tmp_path / "d"))
    rag.remember("Como fazer deploy com Docker", "Use Dockerfile e docker-compose.")
    rag.remember("Qual horario do cafe", "Por volta das 9h.")
    hits = rag.retrieve("preciso de ajuda com Docker deploy", top_k=2, min_similarity=0.05)
    assert hits, "busca semântica deveria retornar resultados"
    assert "Docker" in hits[0]["text"]

def test_feedback_loop_downranks_bad_response(tmp_path):
    from jarvis.learning.rag import RAGMemory
    rag = RAGMemory(data_dir=str(tmp_path / "d"))
    rag.remember("Deploy Docker bom", "Deploy Docker: Dockerfile, build, compose.")
    rag.remember("Deploy Docker ruim", "Deploy Docker: sei la tenta ai.")
    # Avalia mal a resposta ruim e bem a boa.
    rag.apply_feedback("Deploy Docker ruim", "Deploy Docker: sei la tenta ai.", rating=1)
    rag.apply_feedback("Deploy Docker bom", "Deploy Docker: Dockerfile, build, compose.", rating=5)
    hits = rag.retrieve("deploy Docker", top_k=4, min_similarity=0.05)
    # A memória bem avaliada deve ter effective_score maior que a mal avaliada.
    scores = {h["text"]: h["effective_score"] for h in hits}
    bom = max(v for k, v in scores.items() if "Dockerfile" in k)
    ruim = max(v for k, v in scores.items() if "sei la" in k)
    assert bom > ruim

def test_rating_label_mapping():
    from jarvis.learning.feedback import FeedbackStore
    assert FeedbackStore._rating_to_label(1) == "negative"  # bug histórico corrigido
    assert FeedbackStore._rating_to_label(3) == "neutral"
    assert FeedbackStore._rating_to_label(5) == "positive"

def test_mlp_trainer_learns(tmp_path):
    from jarvis.training.seed_data import write_seed_dataset
    from jarvis.training.mlp_trainer import QualityClassifierTrainer
    path = write_seed_dataset(str(tmp_path / "ds.jsonl"))
    trainer = QualityClassifierTrainer(feature_dim=256, hidden_dim=32)
    result = trainer.train(path, epochs=80, verbose=False)
    # A rede deve aprender o treino (loss baixa, acurácia alta).
    assert result["final_train_acc"] >= 0.8
    pred = trainer.predict("USER: How to deploy?\nJARVIS: Just do it somehow.")
    assert pred["label"] == "negative"

def test_memory_migration_is_idempotent(tmp_path):
    import sqlite3
    from scripts.migrate_memory import migrate
    old = str(tmp_path / "old.db")
    conn = sqlite3.connect(old)
    conn.execute("CREATE TABLE episodes (id INTEGER PRIMARY KEY, timestamp TEXT, "
                 "event_type TEXT, user_input TEXT, jarvis_response TEXT, "
                 "context JSON, emotional_state TEXT, learned_insight TEXT)")
    conn.execute("INSERT INTO episodes (timestamp,event_type,user_input,jarvis_response,context,emotional_state) "
                 "VALUES ('2024','DEPLOY','p Docker','r','{}','neutral')")
    conn.commit(); conn.close()
    data_dir = str(tmp_path / "data")
    r1 = migrate(old, data_dir)
    r2 = migrate(old, data_dir)
    assert r1["migrated"] == 1
    assert r2["migrated"] == 0 and r2["skipped_already_present"] == 1
