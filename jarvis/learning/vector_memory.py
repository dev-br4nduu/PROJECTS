"""
Vector Memory — real semantic long-term memory with cosine retrieval.

This replaces the LIKE-based text search in core/memory.py with genuine
semantic retrieval:

  - every stored memory is embedded to a vector
  - retrieval embeds the query and ranks memories by cosine similarity
  - vectors persist to disk (numpy .npy) alongside metadata (SQLite)

Scale note: this does an exact brute-force cosine search in numpy, which is
fine and fast up to ~100k memories. Beyond that you'd swap in FAISS/Qdrant —
the interface here is designed so that swap is localized to this file.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json
import sqlite3
import numpy as np

from jarvis.learning.embeddings import get_embedding_backend


class VectorMemory:
    """Semantic memory store backed by embeddings + cosine similarity."""

    def __init__(self, data_dir: str = "jarvis_data",
                 db_name: str = "vector_memory.db",
                 prefer_neural: bool = True):
        os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, db_name)
        # Namespace the vectors file by db_name so multiple stores can coexist
        # in the same data_dir without clobbering each other's vectors.
        stem = os.path.splitext(db_name)[0]
        self.vectors_path = os.path.join(data_dir, f"{stem}_vectors.npy")

        self.backend = get_embedding_backend(prefer_neural=prefer_neural)
        self.embedding_backend_name = self.backend.name

        # In-memory matrix of shape [n_memories, dim]; mirrored to disk.
        self._vectors: Optional[np.ndarray] = None
        self._ids: List[int] = []

        self._init_db()
        self._load_vectors()
        # For TF-IDF backend we must (re)fit on existing corpus so encode works.
        self._ensure_backend_fitted()

    # ---------- persistence ----------

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                role TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _load_vectors(self) -> None:
        if os.path.exists(self.vectors_path):
            self._vectors = np.load(self.vectors_path)
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT id FROM memories ORDER BY id ASC").fetchall()
        conn.close()
        self._ids = [r[0] for r in rows]

    def _save_vectors(self) -> None:
        if self._vectors is not None:
            np.save(self.vectors_path, self._vectors)

    def _all_texts(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT text FROM memories ORDER BY id ASC").fetchall()
        conn.close()
        return [r[0] for r in rows]

    def _ensure_backend_fitted(self) -> None:
        """TF-IDF backend needs a corpus fit; neural backend is a no-op."""
        if getattr(self.backend, "is_fitted", True):
            return
        corpus = self._all_texts()
        if corpus:
            self.backend.fit(corpus)
            # Re-embed existing corpus so stored vectors match the fitted space.
            self._rebuild_all_vectors(corpus)

    def _rebuild_all_vectors(self, corpus: List[str]) -> None:
        if not corpus:
            return
        self._vectors = self.backend.encode(corpus)
        self._save_vectors()

    # ---------- public API ----------

    def add(self, text: str, role: str = "user",
            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store a memory and index its embedding."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute(
            "INSERT INTO memories (text, role, metadata, created_at) VALUES (?,?,?,?)",
            (text, role, json.dumps(metadata or {}), datetime.now().isoformat()),
        )
        mem_id = cur.lastrowid
        conn.commit()
        conn.close()

        # TF-IDF backend: a new term may require refitting the space. Refit lazily
        # once the corpus grows, otherwise just transform.
        if not getattr(self.backend, "is_fitted", True):
            corpus = self._all_texts()
            self.backend.fit(corpus)
            self._rebuild_all_vectors(corpus)
            self._ids = self._current_ids()
            return {"id": mem_id, "indexed": True, "backend": self.backend.name}

        vec = self.backend.encode([text])  # shape [1, dim]
        if self._vectors is None:
            self._vectors = vec
        else:
            # Dimension can drift for TF-IDF after refits; guard it.
            if vec.shape[1] != self._vectors.shape[1]:
                corpus = self._all_texts()
                self._rebuild_all_vectors(corpus)
            else:
                self._vectors = np.vstack([self._vectors, vec])
        self._ids.append(mem_id)
        self._save_vectors()
        return {"id": mem_id, "indexed": True, "backend": self.backend.name}

    def search(self, query: str, top_k: int = 5,
               min_similarity: float = 0.0) -> List[Dict[str, Any]]:
        """Return the top_k most semantically similar memories to the query."""
        if self._vectors is None or len(self._ids) == 0:
            return []
        if not getattr(self.backend, "is_fitted", True):
            self._ensure_backend_fitted()
            if self._vectors is None:
                return []

        qvec = self.backend.encode([query])[0]  # [dim]
        # Cosine similarity == dot product (vectors are L2-normalized).
        sims = self._vectors @ qvec  # [n]
        order = np.argsort(-sims)[:top_k]

        results = []
        conn = sqlite3.connect(self.db_path)
        for idx in order:
            score = float(sims[idx])
            if score < min_similarity:
                continue
            mem_id = self._ids[idx]
            row = conn.execute(
                "SELECT text, role, metadata, created_at FROM memories WHERE id=?",
                (mem_id,),
            ).fetchone()
            if row:
                results.append({
                    "id": mem_id,
                    "text": row[0],
                    "role": row[1],
                    "metadata": json.loads(row[2]),
                    "created_at": row[3],
                    "similarity": round(score, 4),
                })
        conn.close()
        return results

    def _current_ids(self) -> List[int]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT id FROM memories ORDER BY id ASC").fetchall()
        conn.close()
        return [r[0] for r in rows]

    def stats(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        conn.close()
        return {
            "total_memories": count,
            "embedding_backend": self.embedding_backend_name,
            "vector_dim": int(self._vectors.shape[1]) if self._vectors is not None else 0,
            "index_size": len(self._ids),
        }
