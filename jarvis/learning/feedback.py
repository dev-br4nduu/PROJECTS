"""
Feedback Capture — the fuel for all learning.

Records two kinds of signal, both persisted to SQLite:

  1. Explicit feedback  : user rates a response (👍/👎 or 1-5), optional correction text.
  2. Implicit feedback  : behavioral signals (user rephrased, accepted, copied, etc.).

From this it can emit:
  - a supervised dataset (text -> label) for training a quality/intent classifier
  - preference pairs (prompt, chosen, rejected) for DPO-style preference training

Nothing here is simulated — every row is real data captured from real interactions
and every export is a real training file.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json
import sqlite3


class FeedbackStore:
    """Persistent store for interaction feedback and preference pairs."""

    def __init__(self, data_dir: str = "jarvis_data", db_name: str = "feedback.db"):
        os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, db_name)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                rating INTEGER,               -- 1..5, or 1/0 for thumbs
                label TEXT,                   -- 'positive' | 'negative' | 'neutral'
                correction TEXT,              -- user's improved answer, if any
                signal_type TEXT,             -- 'explicit' | 'implicit'
                implicit_signal TEXT,         -- e.g. 'rephrased', 'accepted', 'copied'
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS preference_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                chosen TEXT NOT NULL,
                rejected TEXT NOT NULL,
                source TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    # ---------- explicit ----------

    def record_explicit(self, prompt: str, response: str, rating: int,
                        correction: Optional[str] = None) -> Dict[str, Any]:
        """
        Record an explicit rating. rating: 1-5 (or 1/0 thumbs).
        A correction (user's better answer) automatically creates a preference pair.
        """
        label = self._rating_to_label(rating)
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            INSERT INTO interactions
            (prompt, response, rating, label, correction, signal_type, created_at)
            VALUES (?,?,?,?,?, 'explicit', ?)
        """, (prompt, response, rating, label, correction, datetime.now().isoformat()))
        interaction_id = cur.lastrowid
        conn.commit()
        conn.close()

        # A correction is a gold preference pair: correction > original response.
        if correction:
            self.add_preference_pair(prompt, chosen=correction,
                                     rejected=response, source="user_correction")

        return {"id": interaction_id, "label": label, "signal_type": "explicit"}

    def record_implicit(self, prompt: str, response: str,
                       implicit_signal: str) -> Dict[str, Any]:
        """
        Record a behavioral signal. Maps common signals to a weak label:
          accepted/copied -> positive ; rephrased/ignored -> negative
        """
        positive_signals = {"accepted", "copied", "followed_up_positively", "saved"}
        negative_signals = {"rephrased", "ignored", "abandoned", "retried"}
        if implicit_signal in positive_signals:
            label = "positive"
        elif implicit_signal in negative_signals:
            label = "negative"
        else:
            label = "neutral"

        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            INSERT INTO interactions
            (prompt, response, label, signal_type, implicit_signal, created_at)
            VALUES (?,?,?, 'implicit', ?, ?)
        """, (prompt, response, label, implicit_signal, datetime.now().isoformat()))
        interaction_id = cur.lastrowid
        conn.commit()
        conn.close()
        return {"id": interaction_id, "label": label, "signal_type": "implicit"}

    def add_preference_pair(self, prompt: str, chosen: str, rejected: str,
                           source: str = "manual") -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            INSERT INTO preference_pairs (prompt, chosen, rejected, source, created_at)
            VALUES (?,?,?,?,?)
        """, (prompt, chosen, rejected, source, datetime.now().isoformat()))
        pair_id = cur.lastrowid
        conn.commit()
        conn.close()
        return {"id": pair_id, "source": source}

    # ---------- dataset export ----------

    def export_classification_dataset(self) -> List[Dict[str, str]]:
        """
        Export (text, label) rows for training a response-quality classifier.
        text = prompt + response ; label = positive/negative/neutral.
        """
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("""
            SELECT prompt, response, label FROM interactions
            WHERE label IS NOT NULL
        """).fetchall()
        conn.close()
        return [
            {"text": f"USER: {p}\nJARVIS: {r}", "label": lbl}
            for (p, r, lbl) in rows
        ]

    def export_preference_pairs(self) -> List[Dict[str, str]]:
        """Export (prompt, chosen, rejected) rows for DPO-style training."""
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("""
            SELECT prompt, chosen, rejected FROM preference_pairs
        """).fetchall()
        conn.close()
        return [{"prompt": p, "chosen": c, "rejected": r} for (p, c, r) in rows]

    def write_jsonl(self, kind: str = "classification",
                    out_path: Optional[str] = None) -> str:
        """Write a dataset to JSONL on disk. kind: 'classification' | 'preference'."""
        if kind == "classification":
            data = self.export_classification_dataset()
            default = "dataset_classification.jsonl"
        elif kind == "preference":
            data = self.export_preference_pairs()
            default = "dataset_preference.jsonl"
        else:
            raise ValueError("kind must be 'classification' or 'preference'")

        out_path = out_path or os.path.join(self.data_dir, default)
        with open(out_path, "w") as f:
            for row in data:
                f.write(json.dumps(row) + "\n")
        return out_path

    @staticmethod
    def _rating_to_label(rating: int) -> str:
        """
        Mapeia rating numa escala 1-5 para rótulo.
        Para polegar, o chamador deve mapear: 👍 -> 5, 👎 -> 1.
        (Antes havia um bug que tratava rating==1 como polegar-para-cima.)
        """
        if rating is None:
            return "neutral"
        if rating >= 4:
            return "positive"
        if rating <= 2:
            return "negative"
        return "neutral"

    def stats(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        total = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        pos = conn.execute("SELECT COUNT(*) FROM interactions WHERE label='positive'").fetchone()[0]
        neg = conn.execute("SELECT COUNT(*) FROM interactions WHERE label='negative'").fetchone()[0]
        pairs = conn.execute("SELECT COUNT(*) FROM preference_pairs").fetchone()[0]
        conn.close()
        return {
            "total_interactions": total,
            "positive": pos,
            "negative": neg,
            "neutral": total - pos - neg,
            "preference_pairs": pairs,
        }
