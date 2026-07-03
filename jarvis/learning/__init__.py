"""
Real Learning Module — RAG memory, feedback capture, and model training.

Diferente dos módulos conceituais das fases 3-5, este pacote implementa
aprendizado REAL e funcional:
  - embeddings.py      : geração de embeddings (sentence-transformers ou TF-IDF)
  - vector_memory.py   : memória vetorial com busca semântica por similaridade
  - feedback.py        : captura de feedback explícito/implícito e pares de preferência
  - rag.py             : orquestra memória + feedback para melhorar respostas
"""
