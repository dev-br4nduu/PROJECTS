#!/usr/bin/env python3
"""
Migração de memória: banco de episódios antigo -> índice vetorial novo.

A versão antiga do JARVIS guardava episódios em `jarvis_memory.db` (tabela
`episodes`) e buscava com LIKE textual. A versão nova indexa cada episódio num
store vetorial para busca semântica. Este script lê os episódios antigos e os
re-registra pela API nova (que os embeda e indexa), sem perder nada.

É IDEMPOTENTE: episódios já migrados (mesmo timestamp + user_input) são pulados,
então rodar duas vezes não duplica dados.

Uso:
    python scripts/migrate_memory.py                       # usa caminhos padrão
    python scripts/migrate_memory.py --old jarvis_memory.db --data-dir jarvis_data
"""

from __future__ import annotations
import argparse
import os
import sqlite3
import sys

# Garante que o pacote jarvis é importável ao rodar como script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.memory import EpisodicMemory


def _read_old_episodes(old_db: str):
    """Lê episódios do banco antigo. Retorna [] se o banco/tabela não existir."""
    if not os.path.exists(old_db):
        return []
    conn = sqlite3.connect(old_db)
    try:
        # Confirma que a tabela existe antes de consultar.
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='episodes'"
        ).fetchone()
        if not exists:
            return []
        rows = conn.execute(
            "SELECT timestamp, event_type, user_input, jarvis_response, "
            "context, emotional_state FROM episodes ORDER BY id ASC"
        ).fetchall()
    finally:
        conn.close()
    return rows


def migrate(old_db: str = "jarvis_memory.db", data_dir: str = "jarvis_data") -> dict:
    old_episodes = _read_old_episodes(old_db)
    if not old_episodes:
        return {"status": "nothing_to_migrate", "old_db": old_db, "migrated": 0}

    mem = EpisodicMemory(data_dir=data_dir)

    # Conjunto de chaves já presentes, para idempotência. Chave = conteúdo
    # (pergunta + resposta), pois o timestamp é regerado ao re-registrar.
    existing = set()
    conn = sqlite3.connect(mem.db_path)
    for ui, resp in conn.execute("SELECT user_input, jarvis_response FROM episodes").fetchall():
        existing.add((ui, resp))
    conn.close()

    migrated, skipped = 0, 0
    import json
    for ts, event_type, user_input, response, context, emotional in old_episodes:
        if (user_input, response) in existing:
            skipped += 1
            continue
        try:
            ctx = json.loads(context) if context else {}
        except (json.JSONDecodeError, TypeError):
            ctx = {}
        ctx.setdefault("emotional_state", emotional or "neutral")
        ctx["migrated_from"] = old_db
        mem.record_episode(event_type or "MIGRATED", user_input or "", response or "", ctx)
        migrated += 1

    return {
        "status": "ok",
        "old_db": old_db,
        "data_dir": data_dir,
        "found": len(old_episodes),
        "migrated": migrated,
        "skipped_already_present": skipped,
    }


def main():
    parser = argparse.ArgumentParser(description="Migra episódios antigos para o índice vetorial")
    parser.add_argument("--old", default="jarvis_memory.db", help="banco de episódios antigo")
    parser.add_argument("--data-dir", default="jarvis_data", help="diretório de dados novo")
    args = parser.parse_args()

    result = migrate(args.old, args.data_dir)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
