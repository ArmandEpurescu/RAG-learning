# RAG Learning

A small learning project for Retrieval-Augmented Generation over personal documents.

The current version runs locally with no external dependencies. It indexes Markdown and text files,
searches for relevant chunks with deterministic hashing-based embeddings, and composes an answer
strictly from the retrieved sources. Optionally, it can use a local LLM through Ollama for synthesis.

## Structure

- `data/` - put your `.md` or `.txt` notes and documents here
- `rag/` - application code
- `storage/rag.sqlite3` - local database generated after indexing

## Usage

```powershell
python -m rag ingest data
python -m rag ask "What are the goals of this project?"
```

With a local LLM through Ollama:

```powershell
ollama pull llama3.2:3b
python -m rag ask "What are the goals of this project?" --llm ollama
```

To use another local model:

```powershell
$env:OLLAMA_MODEL="mistral:7b"
python -m rag ask "What are the goals of this project?" --llm ollama
```

OpenAI is still available as an optional provider if you explicitly want it:

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="your-model"
python -m rag ask "What are the goals of this project?" --llm openai
```

## Commands

```powershell
python -m rag ingest data --reset
python -m rag search "rag local" --top-k 5
python -m rag ask "How does the project work?"
```

## How It Works

RAG means Retrieval-Augmented Generation:

1. `ingest` reads documents and splits them into chunks.
2. Each chunk gets a local numeric vector.
3. `ask` turns the question into a vector and searches for nearby chunks.
4. Without `--llm`, the app prints the relevant passages.
5. With `--llm ollama`, the app sends only the retrieved passages to the local model, not the whole collection.

Ollama is the default local path because it exposes a small HTTP API on your machine and avoids paid
API calls. The local model remains configurable through `OLLAMA_MODEL`.
