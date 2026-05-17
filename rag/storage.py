from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredChunk:
    id: int
    path: str
    chunk_index: int
    text: str
    embedding: list[float]


class RagStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        self.connection.close()

    def reset(self) -> None:
        self.connection.execute("DELETE FROM chunks")
        self.connection.commit()

    def delete_document(self, path: str) -> None:
        self.connection.execute("DELETE FROM chunks WHERE path = ?", (path,))

    def add_chunk(self, path: str, chunk_index: int, text: str, embedding: list[float]) -> None:
        self.connection.execute(
            """
            INSERT INTO chunks(path, chunk_index, text, embedding)
            VALUES (?, ?, ?, ?)
            """,
            (path, chunk_index, text, json.dumps(embedding)),
        )

    def commit(self) -> None:
        self.connection.commit()

    def all_chunks(self) -> list[StoredChunk]:
        rows = self.connection.execute(
            "SELECT id, path, chunk_index, text, embedding FROM chunks ORDER BY path, chunk_index"
        ).fetchall()
        return [
            StoredChunk(
                id=row["id"],
                path=row["path"],
                chunk_index=row["chunk_index"],
                text=row["text"],
                embedding=json.loads(row["embedding"]),
            )
            for row in rows
        ]

    def _init_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_chunks_path ON chunks(path)"
        )
        self.connection.commit()

