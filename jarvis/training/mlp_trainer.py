"""
MLP Trainer — a neural network trained from scratch in numpy.

This is real model-weight training: explicit forward pass, cross-entropy loss,
backpropagation, and gradient-descent weight updates. No autograd, no ML
framework — you can read every gradient. It trains a response-quality
classifier (positive / negative / neutral) from the feedback JSONL that the
FeedbackStore exports.

Runs on CPU, offline, in seconds. This is the "train real weights as an ML
exercise" deliverable that actually executes in this environment.

Architecture:
    input (hashed bag-of-features, D dims)
      -> Dense(D, H) + ReLU
      -> Dense(H, C)
      -> softmax
Trained with mini-batch SGD + cross-entropy.
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Optional
import json
import os
import numpy as np

from jarvis.learning.embeddings import HashingBackend


LABELS = ["negative", "neutral", "positive"]
LABEL_TO_IDX = {l: i for i, l in enumerate(LABELS)}


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class MLPClassifier:
    """Two-layer MLP with manual backprop. Weights are real numpy arrays."""

    def __init__(self, input_dim: int, hidden_dim: int = 64,
                 num_classes: int = 3, seed: int = 42):
        rng = np.random.default_rng(seed)
        # He initialization for the ReLU layer.
        self.W1 = rng.standard_normal((input_dim, hidden_dim)) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = rng.standard_normal((hidden_dim, num_classes)) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(num_classes)
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes

    # ---- forward / backward ----

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, Dict]:
        z1 = X @ self.W1 + self.b1
        a1 = np.maximum(0, z1)                 # ReLU
        z2 = a1 @ self.W2 + self.b2
        probs = _softmax(z2)
        cache = {"X": X, "z1": z1, "a1": a1, "probs": probs}
        return probs, cache

    def backward(self, cache: Dict, y_onehot: np.ndarray, lr: float,
                 l2: float = 1e-4) -> None:
        X, a1, probs = cache["X"], cache["a1"], cache["probs"]
        n = X.shape[0]

        # dL/dz2 for softmax + cross-entropy
        dz2 = (probs - y_onehot) / n           # [n, C]
        dW2 = a1.T @ dz2 + l2 * self.W2
        db2 = dz2.sum(axis=0)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * (cache["z1"] > 0)          # ReLU derivative
        dW1 = X.T @ dz1 + l2 * self.W1
        db1 = dz1.sum(axis=0)

        # gradient-descent weight update
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W1 -= lr * dW1
        self.b1 -= lr * db1

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        probs, _ = self.forward(X)
        return probs

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.predict_proba(X).argmax(axis=1)

    # ---- persistence ----

    def save(self, path: str) -> None:
        np.savez(path, W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2,
                 input_dim=self.input_dim, hidden_dim=self.hidden_dim,
                 num_classes=self.num_classes)

    @classmethod
    def load(cls, path: str) -> "MLPClassifier":
        data = np.load(path)
        model = cls(int(data["input_dim"]), int(data["hidden_dim"]),
                    int(data["num_classes"]))
        model.W1, model.b1 = data["W1"], data["b1"]
        model.W2, model.b2 = data["W2"], data["b2"]
        return model


class QualityClassifierTrainer:
    """
    End-to-end trainer: JSONL feedback -> features -> trained weights.

    The featurizer (HashingBackend) is fixed/stateless, so the same features
    are reproducible at inference time.
    """

    def __init__(self, feature_dim: int = 512, hidden_dim: int = 64):
        self.featurizer = HashingBackend(dim=feature_dim)
        self.feature_dim = feature_dim
        self.hidden_dim = hidden_dim
        self.model: Optional[MLPClassifier] = None

    def _load_jsonl(self, path: str) -> Tuple[List[str], List[str]]:
        texts, labels = [], []
        with open(path) as f:
            for line in f:
                row = json.loads(line)
                if row.get("label") in LABEL_TO_IDX:
                    texts.append(row["text"])
                    labels.append(row["label"])
        return texts, labels

    def train(self, dataset_path: str, epochs: int = 200, lr: float = 0.5,
              batch_size: int = 16, val_split: float = 0.2,
              verbose: bool = True) -> Dict:
        texts, labels = self._load_jsonl(dataset_path)
        if len(texts) < 4:
            raise ValueError(
                f"Need at least 4 labeled examples to train, got {len(texts)}. "
                "Collect more feedback first."
            )

        X = self.featurizer.encode(texts)                       # [n, D]
        y = np.array([LABEL_TO_IDX[l] for l in labels])
        y_onehot = np.eye(len(LABELS))[y]

        # train/val split
        rng = np.random.default_rng(0)
        idx = rng.permutation(len(X))
        n_val = max(1, int(len(X) * val_split))
        val_idx, tr_idx = idx[:n_val], idx[n_val:]
        Xtr, ytr, ytr_oh = X[tr_idx], y[tr_idx], y_onehot[tr_idx]
        Xval, yval = X[val_idx], y[val_idx]

        self.model = MLPClassifier(self.feature_dim, self.hidden_dim, len(LABELS))

        history = []
        for epoch in range(epochs):
            # shuffle each epoch
            perm = rng.permutation(len(Xtr))
            Xtr, ytr_oh, ytr = Xtr[perm], ytr_oh[perm], ytr[perm]

            epoch_loss = 0.0
            for start in range(0, len(Xtr), batch_size):
                xb = Xtr[start:start + batch_size]
                yb = ytr_oh[start:start + batch_size]
                probs, cache = self.model.forward(xb)
                # cross-entropy loss
                eps = 1e-9
                loss = -np.mean(np.sum(yb * np.log(probs + eps), axis=1))
                epoch_loss += loss * len(xb)
                self.model.backward(cache, yb, lr)

            epoch_loss /= len(Xtr)
            train_acc = float((self.model.predict(Xtr) == ytr).mean())
            val_acc = float((self.model.predict(Xval) == yval).mean())
            history.append({"epoch": epoch + 1, "loss": round(epoch_loss, 4),
                            "train_acc": round(train_acc, 3),
                            "val_acc": round(val_acc, 3)})
            if verbose and (epoch % max(1, epochs // 10) == 0 or epoch == epochs - 1):
                print(f"epoch {epoch+1:3d}  loss {epoch_loss:.4f}  "
                      f"train_acc {train_acc:.3f}  val_acc {val_acc:.3f}")

        return {
            "examples": len(texts),
            "train_size": len(Xtr),
            "val_size": len(Xval),
            "epochs": epochs,
            "final_train_acc": history[-1]["train_acc"],
            "final_val_acc": history[-1]["val_acc"],
            "final_loss": history[-1]["loss"],
            "history": history,
        }

    def predict(self, text: str) -> Dict:
        if self.model is None:
            raise RuntimeError("Model not trained/loaded.")
        X = self.featurizer.encode([text])
        probs = self.model.predict_proba(X)[0]
        idx = int(probs.argmax())
        return {
            "label": LABELS[idx],
            "confidence": round(float(probs[idx]), 3),
            "distribution": {LABELS[i]: round(float(probs[i]), 3) for i in range(len(LABELS))},
        }

    def save(self, path: str) -> None:
        if self.model is None:
            raise RuntimeError("Nothing to save.")
        self.model.save(path)

    def load(self, path: str) -> None:
        self.model = MLPClassifier.load(path)
