from __future__ import annotations

from pathlib import Path

from .chunking import chunk_text
from .embedding import embed
from .storage import RagStore

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def iter_documents(root: Path) -> list[Path]:
    if root.is_file() and root.suffix.lower() in SUPPORTED_EXTENSIONS:
        return [root]
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def ingest_path(store: RagStore, root: Path, reset: bool = False) -> int:
    if reset:
        store.reset()

    documents = iter_documents(root)
    chunk_count = 0

    for document in documents:
        display_path = str(document.as_posix())
        store.delete_document(display_path)
        text = document.read_text(encoding="utf-8")
        for chunk_index, chunk in enumerate(chunk_text(text), start=1):
            store.add_chunk(display_path, chunk_index, chunk.text, embed(chunk.text))
            chunk_count += 1

    store.commit()
    return chunk_count

