# RAG Learning

A small learning project for Retrieval-Augmented Generation over personal documents.

The current version runs locally with no external dependencies. It indexes Markdown and text files,
searches for relevant chunks with deterministic hashing-based embeddings, and composes an answer
strictly from the retrieved sources. Optionally, it can use an LLM through the OpenAI Responses API
for synthesis.

## Structure

- `data/` - put your `.md` or `.txt` notes and documents here
- `rag/` - application code
- `storage/rag.sqlite3` - local database generated after indexing

## Usage

```powershell
python -m rag ingest data
python -m rag ask "What are the goals of this project?"
```

With an LLM:

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="your-model"
python -m rag ask "What are the goals of this project?" --llm
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
5. With `--llm`, the app sends only the retrieved passages to the model, not the whole collection.

The OpenAI Responses API is used for optional synthesis because the official documentation presents
it as the main interface for generating model responses. The model remains configurable through
`OPENAI_MODEL`, so the project is not locked to a model name that may change.
