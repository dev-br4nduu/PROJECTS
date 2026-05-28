"""
Sistema de Memória Episódica e Contextual
Ponto 7: Memória Episódica - lembra interações, entende histórico, correlaciona eventos
"""

from datetime import datetime
from typing import List, Dict, Any
import sqlite3
import json

class EpisodicMemory:
    """Sistema de memória episódica do JARVIS"""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.memory_buffer = []
        self._init_database()

    def _init_database(self):
        """Inicializa banco de dados de memória"""
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
        Registra um episódio na memória

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

        self.memory_buffer.append(episode)
        return episode_id

    def retrieve_context(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Recupera contexto histórico relevante

        Ponto 7: Continuidade operacional
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM episodes
            WHERE user_input LIKE ? OR learned_insight LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f"%{query}%", f"%{query}%", limit))

        episodes = cursor.fetchall()
        conn.close()

        return [self._parse_episode(ep) for ep in episodes]

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
            "context": json.loads(db_row[5]),
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
            "correlations_found": len(self.correlate_events())
        }
