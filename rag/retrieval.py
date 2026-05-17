from __future__ import annotations

from dataclasses import dataclass

from .embedding import cosine_similarity, embed
from .storage import RagStore, StoredChunk


@dataclass(frozen=True)
class SearchResult:
    chunk: StoredChunk
    score: float


def search(store: RagStore, query: str, top_k: int = 5) -> list[SearchResult]:
    query_embedding = embed(query)
    results = [
        SearchResult(chunk=chunk, score=cosine_similarity(query_embedding, chunk.embedding))
        for chunk in store.all_chunks()
    ]
    results.sort(key=lambda result: result.score, reverse=True)
    return results[:top_k]

