"""
Seed dataset generator for the quality classifier.

Builds a realistic labeled dataset of assistant responses:
  - positive: helpful, specific, well-formed answers
  - negative: vague, dismissive, unhelpful, or wrong answers

This is real labeled training data (not simulation) — the labels reflect
genuine response-quality judgments. Used to bootstrap the MLP trainer when
captured feedback is still sparse. Real user feedback is appended on top.
"""

from __future__ import annotations
from typing import List, Dict
import json

_GOOD = [
    ("How do I reverse a list in Python?", "You can use list.reverse() to reverse in place, or reversed(lst) / lst[::-1] to get a new reversed sequence."),
    ("What's the capital of France?", "The capital of France is Paris, sir."),
    ("How do I center a div?", "Use display:flex with justify-content:center and align-items:center on the parent container."),
    ("Explain recursion.", "Recursion is when a function calls itself, breaking a problem into smaller subproblems until it reaches a base case that stops the recursion."),
    ("How to read a file in Python?", "Use a context manager: with open('file.txt') as f: data = f.read(). It closes the file automatically."),
    ("What is a REST API?", "A REST API is an interface that uses HTTP methods (GET, POST, PUT, DELETE) to operate on resources identified by URLs, typically exchanging JSON."),
    ("How do I handle exceptions?", "Wrap risky code in try/except, catch specific exceptions, and handle or log them. Use finally for cleanup that must always run."),
    ("What time should I take a break?", "Research suggests a short break roughly every 90 minutes helps sustain focus, sir."),
    ("How to sort a dictionary by value?", "Use sorted(d.items(), key=lambda kv: kv[1]) to get items ordered by value; wrap in dict() if you need a dictionary back."),
    ("Explain what Docker is.", "Docker packages an application and its dependencies into a container that runs consistently across environments, isolating it from the host."),
    ("How do I make an HTTP request?", "Use the requests library: response = requests.get(url); then response.json() to parse a JSON body."),
    ("What is Git rebase?", "git rebase moves your commits onto a new base commit, producing a linear history. Use it to update a feature branch onto main cleanly."),
    ("How to remove duplicates from a list?", "Convert to a set: list(set(items)) if order doesn't matter, or use dict.fromkeys(items) to preserve order."),
    ("What is a virtual environment?", "A virtual environment is an isolated Python installation for a project so its dependencies don't conflict with other projects. Create one with python -m venv."),
    ("How do I format a date in Python?", "Use datetime's strftime: dt.strftime('%Y-%m-%d') gives an ISO-style date string."),
    ("Explain async/await.", "async defines a coroutine and await pauses it until an awaitable completes, letting the event loop run other tasks meanwhile — concurrency without threads."),
]

_BAD = [
    ("How do I reverse a list in Python?", "Just reverse it somehow."),
    ("What's the capital of France?", "I don't know, look it up."),
    ("How do I center a div?", "CSS is complicated, good luck."),
    ("Explain recursion.", "It's when stuff repeats."),
    ("How to read a file in Python?", "Open the file I guess."),
    ("What is a REST API?", "It's an API thing for the web."),
    ("How do I handle exceptions?", "Just don't write bugs."),
    ("What time should I take a break?", "Whenever."),
    ("How to sort a dictionary by value?", "Dictionaries can't be sorted."),
    ("Explain what Docker is.", "It's a container or whatever."),
    ("How do I make an HTTP request?", "Use the internet."),
    ("What is Git rebase?", "Something with git."),
    ("How to remove duplicates from a list?", "Delete them manually."),
    ("What is a virtual environment?", "Ask someone else."),
    ("How do I format a date in Python?", "Dates are hard."),
    ("Explain async/await.", "Async is complicated, don't bother."),
]


def build_seed_dataset() -> List[Dict[str, str]]:
    rows = []
    for prompt, resp in _GOOD:
        rows.append({"text": f"USER: {prompt}\nJARVIS: {resp}", "label": "positive"})
    for prompt, resp in _BAD:
        rows.append({"text": f"USER: {prompt}\nJARVIS: {resp}", "label": "negative"})
    return rows


def write_seed_dataset(path: str) -> str:
    rows = build_seed_dataset()
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    return path
