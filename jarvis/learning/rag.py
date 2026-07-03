"""
RAG Orchestrator — ties memory + feedback into the conversation loop.

This is what actually makes JARVIS "learn from talking to you":

  remember(prompt, response)   -> stores the exchange in vector memory
  build_context(query)         -> retrieves relevant past exchanges + learned
                                  preferences, formats them for injection into
                                  the system prompt
  augmented_system_prompt(...) -> returns a system prompt enriched with memory

No model weights change here — this is retrieval-based learning, which is the
correct, real mechanism for an API-backed model like Claude. It works today.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional

from jarvis.learning.vector_memory import VectorMemory
from jarvis.learning.feedback import FeedbackStore


class RAGMemory:
    """Retrieval-augmented memory layer for the assistant."""

    def __init__(self, data_dir: str = "jarvis_data", prefer_neural: bool = True):
        self.memory = VectorMemory(data_dir=data_dir, prefer_neural=prefer_neural)
        self.feedback = FeedbackStore(data_dir=data_dir)

    def remember(self, prompt: str, response: str,
                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store a completed exchange so it can inform future conversations."""
        meta = metadata or {}
        u = self.memory.add(prompt, role="user", metadata=meta)
        a = self.memory.add(response, role="assistant",
                            metadata={**meta, "paired_with": u["id"]})
        return {"user_memory_id": u["id"], "assistant_memory_id": a["id"]}

    def remember_preference(self, statement: str) -> Dict[str, Any]:
        """
        Store an explicit user preference as a first-class memory, e.g.
        'I prefer concise answers' or 'Always address me as sir'.
        """
        return self.memory.add(statement, role="preference",
                               metadata={"kind": "preference"})

    def retrieve(self, query: str, top_k: int = 5,
                 min_similarity: float = 0.15) -> List[Dict[str, Any]]:
        """Return memories semantically relevant to the query."""
        return self.memory.search(query, top_k=top_k, min_similarity=min_similarity)

    def build_context(self, query: str, top_k: int = 5) -> str:
        """Build a text block of relevant memories to inject into a prompt."""
        hits = self.retrieve(query, top_k=top_k)
        if not hits:
            return ""
        lines = []
        prefs = [h for h in hits if h["role"] == "preference"]
        convo = [h for h in hits if h["role"] != "preference"]

        if prefs:
            lines.append("Known user preferences:")
            for p in prefs:
                lines.append(f"  - {p['text']} (relevance {p['similarity']})")
        if convo:
            lines.append("Relevant past context:")
            for c in convo:
                who = "User" if c["role"] == "user" else "You"
                lines.append(f"  - [{who}] {c['text']} (relevance {c['similarity']})")
        return "\n".join(lines)

    def augmented_system_prompt(self, base_prompt: str, query: str,
                                top_k: int = 5) -> str:
        """Enrich a base system prompt with retrieved memory context."""
        context = self.build_context(query, top_k=top_k)
        if not context:
            return base_prompt
        return (
            f"{base_prompt}\n\n"
            f"--- Retrieved memory (use it to personalize and stay consistent) ---\n"
            f"{context}\n"
            f"--- End retrieved memory ---"
        )

    def stats(self) -> Dict[str, Any]:
        return {
            "memory": self.memory.stats(),
            "feedback": self.feedback.stats(),
        }
