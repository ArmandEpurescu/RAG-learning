from __future__ import annotations

from .retrieval import SearchResult


def relevant_results(results: list[SearchResult], min_score: float = 0.05) -> list[SearchResult]:
    return [result for result in results if result.score > min_score]


def answer_from_results(question: str, results: list[SearchResult]) -> str:
    if not results:
        return "No indexed sources found yet. Add files to data/ and run ingest."

    relevant = relevant_results(results)
    if not relevant:
        return "No sufficiently relevant passages were found in the indexed documents."

    lines = [
        f"Question: {question}",
        "",
        "Answer based on retrieved sources:",
    ]

    for index, result in enumerate(relevant, start=1):
        excerpt = result.chunk.text.replace("\n", " ")
        if len(excerpt) > 420:
            excerpt = excerpt[:417].rstrip() + "..."
        lines.append(
            f"{index}. {excerpt} [{result.chunk.path}#{result.chunk.chunk_index}, score={result.score:.3f}]"
        )

    lines.append("")
    lines.append("Note: this is an extractive answer. Use --llm for natural-language synthesis.")
    return "\n".join(lines)
