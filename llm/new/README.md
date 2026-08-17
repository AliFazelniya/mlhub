# Django Docker RAG System

A containerized Retrieval-Augmented Generation (RAG) application for asking grounded questions over uploaded documents. The system combines Django's administration and API capabilities with local semantic retrieval, BM25 keyword retrieval, and OpenRouter-hosted language models.

The project is designed as a practical, inspectable RAG baseline: documents are ingested asynchronously, indexed locally, retrieved through a hybrid strategy, and supplied as context for answer generation.

## Architecture and capabilities

- **Fully Dockerized development environment** — Docker Compose provides a consistent application runtime, while the Dockerfile uses a BuildKit cache mount for pip downloads to speed up repeat builds.
- **Hybrid retrieval** — ChromaDB vector search is merged with BM25 keyword search, improving recall for both semantic queries and exact terminology.
- **Local embeddings and persistent indexes** — the local `all-MiniLM-L6-v2` model generates embeddings; ChromaDB and the BM25 index persist under `chroma_db/`.
- **Resilient tokenization** — BM25 uses NLTK tokenization when its resources are available and falls back to whitespace tokenization if they are not, avoiding ingestion and query failures in constrained environments.
- **Non-blocking ingestion** — document extraction, chunking, embedding, and indexing run in a daemon background thread after upload, keeping Django Admin responsive for large documents.
- **Operational visibility in Admin** — document status and the active ingestion stage are shown in the custom Admin view. Processing records automatically refresh every three seconds until completion or failure.
- **Dark chat interface** — a browser-based chatbot is available at the application root.
- **Supported inputs** — PDF (via PyMuPDF), DOCX, and plain-text documents.

## Technology stack

| Area | Technology |
| --- | --- |
| Web framework and API | Django, Django REST Framework |
| Retrieval | ChromaDB, BM25 (`rank_bm25`), LangChain |
| Document extraction | PyMuPDF, `docx2txt` |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| LLM provider | OpenRouter |
| Runtime and build | Docker, Docker Compose, BuildKit cache mounts |

## Prerequisites

- Docker Engine 20.10+ with Docker Compose v2 (`docker compose`)
- An [OpenRouter API key](https://openrouter.ai/keys)

Verify the local installation:

```bash
docker --version
docker compose version
```

## Installation and setup

1. Clone the repository and enter the project directory.

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create `.env` beside `docker-compose.yml`.

   ```bash
   cp .env.example .env
   ```

   If an example file is not present, create it manually:

   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key
   TOKENIZERS_PARALLELISM=false
   ```

   Keep `.env` out of source control. `OPENROUTER_API_KEY` is required for generating answers; the local embedding model does not require a separate API key.

3. Build and start the application in the background.

   ```bash
   docker compose up -d --build
   ```

   The Dockerfile's `RUN --mount=type=cache` instruction is automatically used by current Docker installations with BuildKit, caching pip artifacts between builds.

4. Apply database migrations and create an administrator account.

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

5. Open the application.

   - Chat interface: [http://localhost:8000/](http://localhost:8000/)
   - Django Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - OpenAPI documentation: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

Upload documents through the **Documents** section of Django Admin. Once the file is saved, track its status and progress message from its change page; wait for the status to become `completed` before relying on its contents in answers.

## API testing

### Ask a question

Send a `POST` request to `/api/ask/` with a JSON `question` field.

```bash
curl --request POST 'http://localhost:8000/api/ask/' \
  --header 'Content-Type: application/json' \
  --data '{"question":"What are the main conclusions in the uploaded documents?"}'
```

Example successful response:

```json
{
  "question": "What are the main conclusions in the uploaded documents?",
  "answer": "...",
  "sources": [
    "example.pdf"
  ]
}
```

If `question` is omitted or empty, the API returns `400 Bad Request`:

```json
{
  "error": "Please provide a question."
}
```

### Postman

Create a request with the following configuration:

| Setting | Value |
| --- | --- |
| Method | `POST` |
| URL | `http://localhost:8000/api/ask/` |
| Header | `Content-Type: application/json` |
| Body | Raw JSON: `{ "question": "Your question" }` |

## Operations

View running containers and application output:

```bash
docker compose ps
docker compose logs -f web
```

Stop the environment while retaining the SQLite database, uploaded documents, and retrieval indexes in the project directory:

```bash
docker compose down
```

## Development notes

- This repository is configured for local development. Before deploying to production, externalize the Django secret key, disable `DEBUG`, configure `ALLOWED_HOSTS`, use a production WSGI/ASGI server, and move SQLite and local index storage to appropriately managed services or durable volumes.
- Background threading is intentionally lightweight for local deployments. For production workloads, use a durable task queue and worker process (for example, Celery) to provide retries, observability, and horizontal scaling.
