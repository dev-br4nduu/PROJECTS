# 🤖 JARVIS — Assistente Pessoal Cognitivo

Assistente pessoal inspirado no J.A.R.V.I.S. da Marvel: chat com o Claude,
**memória de longo prazo real (RAG)**, captura de **feedback** que melhora as
respostas, e um **pipeline de treino de modelo** — além de dezenas de
subsistemas conceituais (segurança, visão, navegação, etc.).

> O foco desta versão é **rodar localmente sem fricção**. O núcleo (chat +
> aprendizado real) funciona com dependências leves, em CPU, offline.

---

## ✅ Pré-requisitos

- **Python 3.10+**
- Uma **chave da API Anthropic** (para o chat) — https://console.anthropic.com/
  - Opcional: a aplicação sobe e serve todos os outros endpoints **sem** a chave.

---

## 🚀 Rodar localmente (3 passos)

```bash
# 1. Ambiente virtual + dependências
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configuração
cp .env.example .env
#   edite .env e coloque sua ANTHROPIC_API_KEY

# 3. Rodar
python run.py
```

Abra **http://localhost:5000** no navegador — a interface do JARVIS carrega ali.

Sem a `ANTHROPIC_API_KEY`, tudo funciona **exceto** o chat, que responde
`503` com uma mensagem clara pedindo a chave.

---

## 🧠 Aprendizado Real (o diferencial)

A cada conversa, o JARVIS:
1. **Recupera** memórias relevantes (preferências + conversas passadas) por
   busca **semântica** (embeddings + similaridade de cosseno) e injeta no prompt.
2. **Responde** com o Claude, já personalizado por esse contexto.
3. **Armazena** a troca na memória vetorial.
4. Com **feedback** (rating 1-5 ou correção), ajusta o score de qualidade: boas
   respostas sobem no ranking, ruins são despriorizadas em buscas futuras.

Detalhes e provas em [`REAL_LEARNING.md`](REAL_LEARNING.md).

### Chat robusto: streaming, prompt caching e erros claros

- **Streaming (SSE):** a UI consome `/api/chat/stream` e mostra a resposta
  token a token; se o navegador não suportar, cai automaticamente para o
  endpoint bloqueante `/api/chat`.
- **Prompt caching:** o system prompt (personalidade fixa do Jarvis) e o
  prefixo da conversa são marcados com `cache_control` seguindo o padrão
  documentado da Anthropic. *Nota honesta:* a Anthropic só efetiva o cache
  acima de um piso de tokens (~1024 para Sonnet/Opus) — o system prompt sozinho
  (~160 tokens) fica abaixo disso, então quem realmente passa a economizar é o
  **prefixo da conversa**, à medida que ela cresce ao longo dos turnos. As
  métricas reais (`cache_read_input_tokens`, `cache_creation_input_tokens`)
  vêm no campo `usage` da resposta de `/api/chat`.
- **Erros específicos da API:** falhas de autenticação, rate limit, timeout e
  indisponibilidade do Claude são mapeadas para o status HTTP correto (401,
  429, 504, 503...) em vez de um 500 genérico.

### Treinar pesos de modelo (exercício de ML)
```bash
# Rede neural treinada do zero em numpy (roda em CPU):
curl -X POST localhost:5000/api/training/train-classifier -d '{"epochs":150}'

# Fine-tuning LoRA de um LLM aberto (requer GPU — ver requirements-ml.txt):
pip install -r requirements-ml.txt
python -m jarvis.training.lora_finetune --mode sft --data jarvis_data/dataset_classification.jsonl
```

---

## 🔁 Utilitários

```bash
# Migrar episódios de uma instalação antiga para o índice vetorial novo:
python scripts/migrate_memory.py --old jarvis_memory.db --data-dir jarvis_data
```

---

## 🐳 Docker (opcional)

```bash
docker compose up --build      # sobe JARVIS + Redis + PostgreSQL + Nginx
```

---

## 📚 Principais endpoints

| Rota | Descrição |
|------|-----------|
| `GET /` | Interface web do JARVIS |
| `GET /health` | Health check (JSON) |
| `GET /api` | Metadata e contagem de endpoints |
| `POST /api/chat` | Conversa com o Claude (bloqueante, usa memória) |
| `POST /api/chat/stream` | Mesmo chat, em streaming (SSE) |
| `POST /api/rag/search` | Busca semântica na memória |
| `POST /api/rag/remember-preference` | Registra uma preferência |
| `POST /api/feedback/explicit` | Feedback (rating/correção) → ajusta memória |
| `POST /api/memory/search` | Busca semântica nos episódios |
| `POST /api/training/train-classifier` | Treina a rede neural (CPU) |

Referência completa: [`API_QUICK_REFERENCE.md`](API_QUICK_REFERENCE.md).

---

## 📁 Estrutura

```
jarvis/
├── app.py                 # API Flask (119 endpoints) + serve a UI
├── ai_engine.py           # Chat com Claude + memória RAG
├── config.py              # Configuração (lê .env)
├── learning/              # * Aprendizado real: embeddings, memória vetorial,
│                          #   feedback, RAG
├── training/              # * Treino de pesos: MLP (numpy) + LoRA (LLM aberto)
├── core/                  # Subsistemas cognitivos (memória, segurança, etc.)
├── voice/ vision/ …       # Subsistemas conceituais (fases 2.5–5.0)
└── enterprise/ singularity/
static/                    # Interface web (HTML/CSS/JS)
scripts/                   # Utilitários (migração de memória)
requirements.txt           # Dependências do núcleo (leves, CPU)
requirements-ml.txt        # Dependências opcionais de GPU (LoRA)
```

> **Nota de honestidade:** os subsistemas das fases 3–5 (`singularity/`,
> partes de `enterprise/`, `voice/`, `vision/`) são **conceituais** — expõem a
> arquitetura e a API, mas retornam valores simulados. O que é **real e
> testado** é o núcleo: chat, memória RAG, feedback e treino do classificador.

---

## 📄 Licença

Projeto pessoal.
