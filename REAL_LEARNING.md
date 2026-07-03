# 🧠 JARVIS — Aprendizado Real (RAG + Feedback + Treino de Pesos)

Diferente dos módulos conceituais das fases 3–5 (que retornam valores
simulados), **este subsistema é real e roda de fato**. Foi testado ponta a
ponta em CPU, offline.

Dois blocos, exatamente como planejado:

1. **RAG + Feedback** — JARVIS fica melhor conversando e lembrando de você.
2. **Treino de pesos** — rede neural treinada do zero (roda aqui) + fine-tuning
   LoRA de um LLM aberto (para ambiente com GPU).

---

## 1. RAG — Memória Semântica de Longo Prazo

**Pacote:** `jarvis/learning/`

| Arquivo | O que faz |
|---------|-----------|
| `embeddings.py` | Converte texto → vetor. Backend neural (sentence-transformers) se disponível; senão **HashingVectorizer** (word + char n-grams, 1024-d, offline, sem fit). |
| `vector_memory.py` | Guarda memórias + vetores, busca por **similaridade de cosseno** real. Persiste em SQLite + `.npy`. |
| `feedback.py` | Captura feedback explícito/implícito e gera datasets de treino. |
| `rag.py` | Orquestra tudo: `remember()`, `retrieve()`, `augmented_system_prompt()`. |

O `ai_engine.py` agora, a cada mensagem:
1. Recupera memórias relevantes (preferências + conversas passadas) e injeta no system prompt.
2. Chama o Claude com esse prompt aumentado.
3. Armazena a nova troca na memória vetorial.

**É assim que ele "aprende" com você** — sem treinar pesos, que é o mecanismo
correto para um modelo servido por API como o Claude.

### Prova (testado)
```
Query: "me lembra do meu projeto Flask"
  [0.620] Meu projeto usa Flask e PostgreSQL   ← recuperado por similaridade real
```

### Limitação honesta
O backend offline (hashing) casa por **sobreposição de termos** (Flask↔Flask,
senhor↔senhor). Ele **não** sabe que "banco de dados"≈"PostgreSQL" — isso exige
o backend neural (sentence-transformers), que aqui é bloqueado pela política de
rede (HuggingFace 403). Onde houver acesso, basta descomentar no
`requirements.txt` e o sistema usa embeddings neurais automaticamente.

---

## 2. Feedback — o Combustível do Aprendizado

- **Explícito:** rating 1–5 + correção opcional. Uma correção vira
  automaticamente um **par de preferência** (`chosen` > `rejected`).
- **Implícito:** sinais de comportamento (`accepted`, `rephrased`, `copied`…).
- **Export:** gera `dataset_classification.jsonl` e `dataset_preference.jsonl`
  — arquivos de treino reais.

---

## 3. Treino de Pesos — Rede Neural do Zero (roda AQUI)

**Arquivo:** `jarvis/training/mlp_trainer.py`

Uma MLP de 2 camadas treinada **from scratch em numpy** — forward, cross-entropy,
**backprop e gradient descent explícitos** (dá pra ler cada gradiente). Treina um
classificador de qualidade de resposta a partir do feedback.

### Prova (testado, CPU, ~segundos)
```
epoch   1  loss 1.0727  train_acc 0.538
epoch 150  loss 0.0050  train_acc 1.000     ← loss cai, pesos aprendem

Inferência em respostas NOVAS (não vistas):
  [positive 91%] "Machine learning trains models on data..."
  [negative 99%] "Its some AI thing idk."
```

Isto é ML de verdade: pesos atualizados por gradiente, generalizando para
exemplos novos. Pesos salvos em `.npz`.

### Uso
```bash
# via API
curl -X POST localhost:5000/api/training/train-classifier -d '{"epochs":150}'
curl -X POST localhost:5000/api/training/predict-quality \
     -d '{"text":"USER: ...\nJARVIS: ..."}'
```

---

## 4. Treino de Pesos — LoRA num LLM Aberto (requer GPU)

**Arquivo:** `jarvis/training/lora_finetune.py`

Treina os **pesos reais de um transformer** (via adapters LoRA) nos dados que o
JARVIS coleta. O Claude não pode ser treinado — mas um modelo aberto
(Qwen/Llama/Mistral) pode. Dois modos:

- **SFT** — aprende com boas conversas (rating positivo).
- **DPO** — aprende a preferir `chosen` sobre `rejected` (dos pares de correção).

```bash
pip install -r requirements-ml.txt   # só em ambiente com GPU + acesso a modelos
python -m jarvis.training.lora_finetune --mode sft --data jarvis_data/dataset_classification.jsonl
python -m jarvis.training.lora_finetune --mode dpo --data jarvis_data/dataset_preference.jsonl
```

O import é *dependency-guarded*: o resto do JARVIS roda normalmente mesmo sem o
stack pesado; o erro só aparece se você chamar o treino sem GPU/libs.

---

## Endpoints Novos (11)

| Método | Rota | Função |
|--------|------|--------|
| POST | `/api/rag/remember` | Armazena troca na memória |
| POST | `/api/rag/remember-preference` | Registra preferência |
| POST | `/api/rag/search` | Busca semântica |
| POST | `/api/rag/context` | Contexto p/ injeção no prompt |
| GET  | `/api/rag/stats` | Estatísticas memória+feedback |
| POST | `/api/feedback/explicit` | Feedback com rating/correção |
| POST | `/api/feedback/implicit` | Sinal implícito |
| POST | `/api/feedback/export/<kind>` | Exporta dataset JSONL |
| POST | `/api/training/train-classifier` | Treina rede neural (CPU) |
| POST | `/api/training/predict-quality` | Prediz qualidade de resposta |
| GET  | `/api/training/lora-info` | Como rodar LoRA (GPU) |

---

## Como o ciclo se fecha (aprendizado constante)

```
conversa → memória vetorial ─┐
                             ├─► respostas melhores e personalizadas (RAG)
feedback/correções ──────────┘
      │
      └─► datasets JSONL ──► treino de pesos (MLP agora / LoRA c/ GPU)
                                     │
                                     └─► modelo que reflete seu estilo
```

Cada interação alimenta a memória e o dataset; cada treino melhora o modelo.
Esse é o loop de **aprendizado contínuo** — real, não simulado.
