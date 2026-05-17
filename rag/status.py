from __future__ import annotations

import os
from pathlib import Path

from .llm import LlmError, fetch_ollama_models, load_ollama_config, load_openai_config
from .storage import RagStore


def build_status_report(store: RagStore, db_path: Path) -> str:
    store_stats = store.stats()
    ollama = load_ollama_config()
    openai_configured = bool(os.environ.get("OPENAI_API_KEY")) and bool(os.environ.get("OPENAI_MODEL"))

    lines = [
        "RAG Learning status",
        "",
        "Index",
        f"- database: {db_path}",
        f"- documents: {store_stats['documents']}",
        f"- chunks: {store_stats['chunks']}",
        "",
        "Ollama",
        f"- base URL: {ollama.base_url}",
        f"- configured model: {ollama.model}",
    ]

    try:
        models = fetch_ollama_models(ollama)
    except LlmError as error:
        lines.append(f"- server: unavailable ({error})")
    else:
        lines.append("- server: available")
        if models:
            lines.append(f"- installed models: {', '.join(models)}")
            lines.append(f"- configured model installed: {'yes' if ollama.model in models else 'no'}")
        else:
            lines.append("- installed models: none")
            lines.append("- configured model installed: no")

    lines.extend(
        [
            "",
            "OpenAI",
            f"- configured: {'yes' if openai_configured else 'no'}",
        ]
    )

    if openai_configured:
        try:
            openai = load_openai_config()
        except LlmError as error:
            lines.append(f"- configuration error: {error}")
        else:
            lines.append(f"- model: {openai.model}")
            lines.append(f"- base URL: {openai.base_url}")

    return "\n".join(lines)
