from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from .retrieval import SearchResult


class LlmError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str
    base_url: str = "https://api.openai.com/v1"


def load_openai_config() -> OpenAIConfig:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("OPENAI_MODEL", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()

    if not api_key:
        raise LlmError("Missing OPENAI_API_KEY.")
    if not model:
        raise LlmError("Missing OPENAI_MODEL.")

    return OpenAIConfig(api_key=api_key, model=model, base_url=base_url.rstrip("/"))


def build_rag_prompt(question: str, results: list[SearchResult]) -> str:
    context_blocks = []
    for index, result in enumerate(results, start=1):
        context_blocks.append(
            "\n".join(
                [
                    f"[{index}] Source: {result.chunk.path}#{result.chunk.chunk_index}",
                    f"Score: {result.score:.3f}",
                    result.chunk.text,
                ]
            )
        )

    return "\n\n".join(
        [
            "Answer the question using only the context below.",
            "If the information is not in the context, clearly say you do not know from the indexed documents.",
            "Cite relevant sources in [n] format.",
            "",
            f"Question: {question}",
            "",
            "Context:",
            "\n\n".join(context_blocks),
        ]
    )


def synthesize_with_openai(question: str, results: list[SearchResult]) -> str:
    config = load_openai_config()
    payload = {
        "model": config.model,
        "instructions": "You are a concise, careful, source-grounded RAG assistant.",
        "input": build_rag_prompt(question, results),
        "store": False,
    }

    request = urllib.request.Request(
        url=f"{config.base_url}/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise LlmError(f"OpenAI API returned HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise LlmError(f"Could not contact the LLM provider: {error.reason}") from error

    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content.get("text", ""))

    text = "\n".join(part.strip() for part in parts if part.strip())
    if not text:
        raise LlmError("The LLM provider did not return text.")
    return text
