# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python CLI for PDF ingestion and retrieval-augmented search using LangChain, PostgreSQL, and pgVector.

- Ingest `document.pdf`, split it into chunks, create embeddings, and persist vectors in pgVector.
- Ask one question through `src/chat.py`; retrieve the 10 most similar chunks and ask Gemini to answer only from that context.
- Prompt requires this exact out-of-context response: `Não tenho informações necessárias para responder sua pergunta.`

## Architecture

- `src/load.py`: shared PGVector loader. Creates `GoogleGenerativeAIEmbeddings` and returns a `PGVector` store from `DATABASE_URL`, `PG_VECTOR_COLLECTION_NAME`, and `use_jsonb=True`.
- `src/ingest.py`: loads the PDF with `PyPDFLoader`, splits documents with `RecursiveCharacterTextSplitter` using `chunk_size=1000` and `chunk_overlap=150`, removes empty metadata values, assigns IDs as `doc-{index}`, and adds documents to the shared store.
- `src/search.py`: defines the Portuguese context-only prompt, retrieves 10 similar documents, formats the prompt, and invokes `ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)`.
- `src/chat.py`: single-question CLI entry point. It reads one question, calls `search_prompt`, and prints `RESPOSTA:`.
- `docker-compose.yml`: starts PostgreSQL 17 with pgVector, exposes port `5432`, mounts `postgres_data`, and runs a one-shot bootstrap container that executes `CREATE EXTENSION IF NOT EXISTS vector;`.

The current implementation uses Gemini embeddings in `src/load.py` and Gemini chat in `src/search.py`. `GOOGLE_EMBEDDING_MODEL` and `OPENAI_*` values in `.env.example` are not read by the current code. Changing embedding models changes vector dimensions; recreate the pgVector collection or reset the PostgreSQL volume before re-ingesting.

## Commands

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `GOOGLE_API_KEY`, `DATABASE_URL`, `PG_VECTOR_COLLECTION_NAME`, and `PDF_PATH`.

```bash
docker compose up -d
python src/ingest.py
python src/chat.py
```

`docker compose down -v` removes the database volume and all stored vectors.

No test suite, lint configuration, or build command is configured. For a basic syntax check, use:

```bash
python -m compileall src
```

## Environment and data

- `.env` is ignored by git; use `.env.example` as the template.
- PostgreSQL defaults are user `postgres`, password `postgres`, database `rag`, and port `5432`.
- The bootstrap service waits for PostgreSQL health before creating the vector extension.
- Ingestion is not idempotent by content: current IDs are based on document order, so repeated ingestion can replace or duplicate stored records depending on store behavior. Inspect current behavior before changing ingestion semantics.
