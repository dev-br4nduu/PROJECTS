"""
Sistema de Memória Episódica e Contextual
Ponto 7: Memória Episódica - lembra interações, entende histórico, correlaciona eventos

Agora com RECUPERAÇÃO SEMÂNTICA real: `retrieve_context` usa a memória vetorial
(embeddings + similaridade de cosseno) em vez da antiga busca textual por LIKE.
A interface pública é a mesma — quem usa esta classe (JarvisOS) não muda.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import sqlite3
import json

from jarvis.learning.vector_memory import VectorMemory


class EpisodicMemory:
    """Sistema de memória episódica do JARVIS com busca semântica."""

    def __init__(self, db_path: str = None, data_dir: str = "jarvis_data"):
        # Mantém compatibilidade: aceita db_path antigo, mas organiza tudo em data_dir.
        os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        self.db_path = db_path or os.path.join(data_dir, "episodic_memory.db")
        self.memory_buffer = []

        # Índice vetorial dedicado aos episódios (namespaced, não colide com o RAG).
        self.vector = VectorMemory(data_dir=data_dir, db_name="episodic_vectors.db")

        self._init_database()

    def _init_database(self):
        """Inicializa banco de dados de memória (fonte de verdade dos episódios)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                event_type TEXT,
                user_input TEXT,
                jarvis_response TEXT,
                context JSON,
                emotional_state TEXT,
                learned_insight TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correlations (
                id INTEGER PRIMARY KEY,
                episode1_id INTEGER,
                episode2_id INTEGER,
                correlation_strength REAL,
                pattern_description TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def record_episode(self, event_type: str, user_input: str,
                      jarvis_response: str, context: Dict) -> int:
        """
        Registra um episódio na memória e o indexa semanticamente.

        Ponto 7: Memória Episódica
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        episode = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_input": user_input,
            "jarvis_response": jarvis_response,
            "context": json.dumps(context),
            "emotional_state": context.get("emotional_state", "neutral"),
            "learned_insight": None
        }

        cursor.execute('''
            INSERT INTO episodes
            (timestamp, event_type, user_input, jarvis_response, context, emotional_state)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (episode["timestamp"], event_type, user_input, jarvis_response,
              episode["context"], episode["emotional_state"]))

        conn.commit()
        episode_id = cursor.lastrowid
        conn.close()

        # Indexa no store vetorial. O texto pesquisável combina input + resposta;
        # o episode_id no metadata liga de volta à fonte de verdade.
        searchable = user_input if not jarvis_response else f"{user_input}\n{jarvis_response}"
        self.vector.add(searchable, role="episode", metadata={
            "episode_id": episode_id,
            "event_type": event_type,
        })

        episode["id"] = episode_id
        self.memory_buffer.append(episode)
        return episode_id

    def retrieve_context(self, query: str, limit: int = 5,
                        min_similarity: float = 0.1) -> List[Dict]:
        """
        Recupera contexto histórico RELEVANTE por similaridade semântica.

        Ponto 7: Continuidade operacional
        Antes: busca textual LIKE. Agora: embeddings + cosseno.
        """
        hits = self.vector.search(query, top_k=limit, min_similarity=min_similarity)
        if not hits:
            return []

        # Junta os episódios pela id guardada no metadata do índice vetorial.
        episode_ids = [h["metadata"].get("episode_id") for h in hits if h["metadata"].get("episode_id")]
        if not episode_ids:
            return []

        conn = sqlite3.connect(self.db_path)
        placeholders = ",".join("?" for _ in episode_ids)
        rows = conn.execute(
            f"SELECT * FROM episodes WHERE id IN ({placeholders})", episode_ids
        ).fetchall()
        conn.close()

        # Mapeia id -> episódio e preserva a ordem por similaridade, anexando o score.
        by_id = {row[0]: self._parse_episode(row) for row in rows}
        results = []
        for h in hits:
            eid = h["metadata"].get("episode_id")
            if eid in by_id:
                ep = by_id[eid]
                ep["similarity"] = h["similarity"]
                results.append(ep)
        return results

    def correlate_events(self) -> List[Dict]:
        """
        Correlaciona eventos na memória

        Ponto 7: Correlaciona eventos
        """
        if len(self.memory_buffer) < 2:
            return []

        correlations = []
        for i in range(len(self.memory_buffer) - 1):
            for j in range(i + 1, len(self.memory_buffer)):
                ep1 = self.memory_buffer[i]
                ep2 = self.memory_buffer[j]

                strength = self._calculate_correlation(ep1, ep2)

                if strength > 0.6:
                    correlations.append({
                        "episode_pair": (i, j),
                        "strength": strength,
                        "pattern": self._identify_pattern(ep1, ep2)
                    })

        return correlations

    def _calculate_correlation(self, ep1: Dict, ep2: Dict) -> float:
        """Calcula força de correlação entre episódios"""
        if ep1["event_type"] == ep2["event_type"]:
            return 0.8
        if ep1["emotional_state"] == ep2["emotional_state"]:
            return 0.5
        return 0.2

    def _identify_pattern(self, ep1: Dict, ep2: Dict) -> str:
        """Identifica padrão entre episódios"""
        if ep1["event_type"] == ep2["event_type"]:
            return f"Recurring {ep1['event_type']} pattern"
        return "Related context"

    def _parse_episode(self, db_row) -> Dict:
        """Converte linha do banco em episódio"""
        return {
            "id": db_row[0],
            "timestamp": db_row[1],
            "event_type": db_row[2],
            "user_input": db_row[3],
            "jarvis_response": db_row[4],
            "context": json.loads(db_row[5]) if db_row[5] else {},
            "emotional_state": db_row[6]
        }

    def get_memory_stats(self) -> Dict:
        """Retorna estatísticas da memória"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM episodes")
        total_episodes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT event_type) FROM episodes")
        event_types = cursor.fetchone()[0]

        conn.close()

        return {
            "total_episodes": total_episodes,
            "event_types": event_types,
            "buffer_size": len(self.memory_buffer),
            "correlations_found": len(self.correlate_events()),
            "semantic_retrieval": True,
            "embedding_backend": self.vector.embedding_backend_name,
        }
