from __future__ import annotations

import hashlib
import math
import re

TOKEN_RE = re.compile(r"[a-zA-Z0-9_ăâîșțĂÂÎȘȚ]+")


def tokenize(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text)]


def embed(text: str, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    tokens = tokenize(text)

    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))

