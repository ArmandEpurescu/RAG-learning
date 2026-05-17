from __future__ import annotations

import argparse
from pathlib import Path

from .answering import answer_from_results, relevant_results
from .ingest import ingest_path
from .llm import LlmError, synthesize
from .retrieval import search
from .storage import RagStore

DEFAULT_DB = Path("storage/rag.sqlite3")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG Learning")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Index markdown and text files")
    ingest.add_argument("path", help="File or directory to index")
    ingest.add_argument("--reset", action="store_true", help="Clear the database first")

    search_parser = subparsers.add_parser("search", help="Search indexed chunks")
    search_parser.add_argument("query")
    search_parser.add_argument("--top-k", type=int, default=5)

    ask = subparsers.add_parser("ask", help="Answer from retrieved context")
    ask.add_argument("question")
    ask.add_argument("--top-k", type=int, default=5)
    ask.add_argument(
        "--llm",
        choices=["ollama", "openai"],
        help="Use an LLM provider for synthesis. Use 'ollama' for local models.",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()
    store = RagStore(Path(args.db))

    try:
        if args.command == "ingest":
            count = ingest_path(store, Path(args.path), reset=args.reset)
            print(f"Indexed {count} chunks into {args.db}")
        elif args.command == "search":
            for result in search(store, args.query, top_k=args.top_k):
                print(f"{result.score:.3f} {result.chunk.path}#{result.chunk.chunk_index}")
                print(result.chunk.text[:300].replace("\n", " "))
                print()
        elif args.command == "ask":
            results = search(store, args.question, top_k=args.top_k)
            if args.llm:
                relevant = relevant_results(results)
                if not relevant:
                    print(answer_from_results(args.question, results))
                    return
                try:
                    print(synthesize(args.question, relevant, provider=args.llm))
                except LlmError as error:
                    print(f"LLM unavailable: {error}")
                    print()
                    print(answer_from_results(args.question, results))
            else:
                print(answer_from_results(args.question, results))
    finally:
        store.close()
