from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    text: str
    start: int
    end: int


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 180) -> list[Chunk]:
    clean = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not clean:
        return []

    chunks: list[Chunk] = []
    start = 0
    text_len = len(clean)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        if end < text_len:
            paragraph_break = clean.rfind("\n\n", start, end)
            sentence_break = clean.rfind(". ", start, end)
            best_break = max(paragraph_break, sentence_break)
            if best_break > start + chunk_size // 2:
                end = best_break + 1

        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(Chunk(text=chunk, start=start, end=end))

        if end >= text_len:
            break
        start = max(0, end - overlap)

    return chunks

