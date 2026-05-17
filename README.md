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
python -m rag status
python -m rag serve
```

## Local API

Start the local app and API server:

```powershell
python -m rag serve --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/
```

The web UI includes chat, retrieval trace, voice input, and optional browser speech output.
Voice input and speech output use browser APIs. The available spoken voices depend on the voices
installed in your browser and operating system.

Ask without streaming:

```powershell
$body = @{
  question = "What are the goals of this project?"
  llm = "ollama"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/ask `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Stream progress and answer tokens with Server-Sent Events:

```powershell
$json = '{"question":"What are the goals of this project?","llm":"ollama"}'
Set-Content -Path .\payload.json -Value $json -NoNewline

curl.exe -N -X POST http://127.0.0.1:8000/ask/stream `
  -H "Content-Type: application/json" `
  --data-binary "@payload.json"
```

The streaming API exposes retrieval progress, source scores, timings, and output tokens. It does not
expose hidden model reasoning.

## How It Works

RAG means Retrieval-Augmented Generation:

1. `ingest` reads documents and splits them into chunks.
2. Each chunk gets a local numeric vector.
3. `ask` turns the question into a vector and searches for nearby chunks.
4. Without `--llm`, the app prints the relevant passages.
5. With `--llm ollama`, the app sends only the retrieved passages to the local model, not the whole collection.

Ollama is the default local path because it exposes a small HTTP API on your machine and avoids paid
API calls. The local model remains configurable through `OLLAMA_MODEL`.

## Personal Context

Add public or non-sensitive notes to `data/`, then reindex:

```powershell
python -m rag ingest data --reset
```

For private notes, use `data/private/`. That folder is ignored by Git. Keep account tokens, Discord
tokens, API keys, and personal secrets out of the public repository.

Potential next integrations:

1. Discord bot that forwards `/ask` messages to the local RAG API.
2. Local safe tools for notes, Git status, and test runs.
3. Path of Exile helper notes and build analysis from indexed local files.
