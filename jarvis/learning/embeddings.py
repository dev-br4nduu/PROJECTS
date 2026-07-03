"""
Embedding backends — real, working text -> vector conversion (offline-capable).

Backends, chosen automatically at runtime:

1. SentenceTransformerBackend  (preferred, if a model is locally available)
   Real neural sentence encoder (all-MiniLM-L6-v2, 384 dims). Requires the
   model to be downloadable/cached. In network-restricted environments this
   may be unavailable, in which case we fall back to (2).

2. HashingBackend  (robust default, always works offline)
   scikit-learn HashingVectorizer combining word (1-2 grams) and character
   (3-5 grams) features into a fixed 1024-dim space. Stateless — needs no
   corpus fit, never degenerates on small data, deterministic. Character
   n-grams give partial morphological matching (deploy ~ deployment). This is
   genuine bag-of-features cosine retrieval — the workhorse of pre-neural IR.

Both expose the same interface:
    backend.encode(texts: list[str]) -> np.ndarray  ([n, dim], L2-normalized)
    backend.fit(corpus)  # no-op for both; kept for API compatibility
"""

from __future__ import annotations
from typing import List
import numpy as np


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    """L2-normalize rows so dot product == cosine similarity."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class SentenceTransformerBackend:
    """Neural sentence embeddings via sentence-transformers (if available)."""

    name = "sentence-transformers"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # lazy import
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.is_fitted = True

    def fit(self, corpus: List[str]) -> None:
        return None

    def encode(self, texts: List[str]) -> np.ndarray:
        vecs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return _l2_normalize(np.asarray(vecs, dtype=np.float32))


class HashingBackend:
    """
    Stateless hashed bag-of-features embeddings. Pure scikit-learn, offline.

    Word features capture topical overlap; character n-grams capture
    morphological similarity (plurals, verb forms, typos). Fixed dimension,
    no fit required, robust from 1 to millions of documents.
    """

    name = "hashing-bow"

    def __init__(self, dim: int = 1024):
        from sklearn.feature_extraction.text import HashingVectorizer

        self.dim = dim
        # Split the space between word and char features.
        self._word_vec = HashingVectorizer(
            n_features=dim // 2, alternate_sign=False,
            analyzer="word", ngram_range=(1, 2), stop_words="english",
            norm=None,
        )
        self._char_vec = HashingVectorizer(
            n_features=dim // 2, alternate_sign=False,
            analyzer="char_wb", ngram_range=(3, 5),
            norm=None,
        )
        self.is_fitted = True  # stateless

    def fit(self, corpus: List[str]) -> None:
        return None

    def encode(self, texts: List[str]) -> np.ndarray:
        # HashingVectorizer handles empty strings poorly; guard them.
        safe = [t if t and t.strip() else " " for t in texts]
        word = self._word_vec.transform(safe).toarray().astype(np.float32)
        char = self._char_vec.transform(safe).toarray().astype(np.float32)
        combined = np.hstack([word, char])
        return _l2_normalize(combined)


def get_embedding_backend(prefer_neural: bool = True, dim: int = 1024):
    """
    Return the best available embedding backend.

    Tries the neural encoder first (real semantics) and transparently falls
    back to the offline hashed bag-of-features backend when the neural model
    can't be loaded (e.g. no network for model download). Both are genuine.
    """
    if prefer_neural:
        try:
            return SentenceTransformerBackend()
        except Exception:
            pass
    return HashingBackend(dim=dim)
