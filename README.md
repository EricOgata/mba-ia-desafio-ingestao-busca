# Ingestão e Busca Semântica com LangChain + PostgreSQL/pgVector

RAG CLI que ingere um PDF, chunka em vetores, persiste no pgVector e responde perguntas via Gemini.

## Arquitetura

```
document.pdf → PyPDFLoader → RecursiveCharacterTextSplitter (1000/150)
       → GoogleGenerativeAIEmbeddings (gemini-embedding-001)
       → PGVector (jsonb)
                ↓
   user question → similarity_search(k=10) → prompt context-only → gemini-2.5-flash → resposta
```

- `src/load.py` — cria `GoogleGenerativeAIEmbeddings` + `PGVector` store
- `src/ingest.py` — carrega PDF, chunka, remove metadados vazios, IDs `doc-{index}`, insere
- `src/search.py` — busca 10 chunks, monta prompt, invoca Gemini, retorna `message.content`
- `src/chat.py` — CLI: lê pergunta, chama `search_prompt`, imprime `RESPOSTA:`

## Pré-requisitos

- Python 3.10+, Docker, Docker Compose
- API key Google (`GOOGLE_API_KEY`)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edite .env: GOOGLE_API_KEY, DATABASE_URL, PG_VECTOR_COLLECTION_NAME, PDF_PATH
docker compose up -d
```

## Uso

```bash
python src/ingest.py    # ingestão única — não é idempotente por conteúdo
python src/chat.py      # loop CLI: PERGUNTA → RESPOSTA
```

Fora do contexto o modelo responde: `Não tenho informações necessárias para responder sua pergunta.`

## Estrutura

```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── document.pdf
├── src/
│   ├── load.py
│   ├── ingest.py
│   ├── search.py
│   └── chat.py
└── README.md
```

## Observações

- Trocar modelo de embedding = dimensão diferente = recriar collection/volume antes de re-ingestar.
- `docker compose down -v` zera dados vetoriais.
- IDs de ingestão baseados em ordem do documento — repetir ingestão pode duplicar/sobrescrever.
