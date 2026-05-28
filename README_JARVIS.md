# 🤖 Jarvis - Personal Assistant

Um assistente pessoal elegante e sofisticado inspirado no Jarvis da Marvel.

## Características

- **Interface Web Elegante**: Design futurista com gradientes azuis e efeitos de vidro fosco
- **Conversação com IA**: Integração com Claude API para respostas inteligentes
- **Histórico de Conversa**: Mantém contexto durante a sessão
- **Personalidade Jarvis**: Ton formal, educado e refinado em inglês britânico
- **Responsivo**: Funciona em desktop e mobile

## Instalação

### 1. Clone o repositório
```bash
git clone <repo-url>
cd projects
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite .env e adicione sua ANTHROPIC_API_KEY
```

### 4. Execute o servidor
```bash
python run.py
```

### 5. Acesse no navegador
```
http://localhost:5000
```

## API Endpoints

### GET `/`
Retorna informações sobre Jarvis

```json
{
  "name": "Jarvis",
  "greeting": "Good day, sir. How may I be of service?",
  "status": "Online and ready to assist"
}
```

### POST `/api/chat`
Envia uma mensagem e recebe resposta

**Request:**
```json
{
  "message": "What is the meaning of life?"
}
```

**Response:**
```json
{
  "user": "What is the meaning of life?",
  "jarvis": "A profound question, sir. The meaning of life is deeply philosophical...",
  "status": "success"
}
```

### GET `/api/history`
Retorna o histórico da conversa

```json
{
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### POST `/api/reset`
Reseta a conversa

```json
{
  "status": "Conversation reset",
  "greeting": "Good day, sir. How may I be of service?"
}
```

## Estrutura do Projeto

```
jarvis/
├── __init__.py           # Pacote principal
├── config.py             # Configurações
├── ai_engine.py          # Motor de IA com Claude
├── app.py                # Aplicação Flask
static/
├── index.html            # Interface web
├── style.css             # Estilos
└── script.js             # JavaScript do cliente
requirements.txt          # Dependências Python
run.py                     # Script para executar
.env.example              # Exemplo de variáveis de ambiente
```

## Personalização

### Mudar a Personalidade do Jarvis

Edite `jarvis/config.py` e modifique `JARVIS_SYSTEM_PROMPT`:

```python
JARVIS_SYSTEM_PROMPT = """
Your custom personality prompt here...
"""
```

### Mudar o Modelo IA

Em `jarvis/ai_engine.py`, altere:

```python
self.model = "claude-3-5-sonnet-20241022"
```

### Customizar a Interface

Edite `static/style.css` para mudar cores, fontes e layout.

## Requisitos

- Python 3.8+
- Chave de API Anthropic (obtém em https://console.anthropic.com)
- Navegador moderno com suporte a ES6

## Licença

Projeto pessoal - Todos os direitos reservados

## Desenvolvido por

PROJECTS Team
