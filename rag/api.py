from __future__ import annotations

import json
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .answering import answer_from_results, relevant_results
from .llm import LlmError, stream_with_ollama, synthesize
from .retrieval import SearchResult, search
from .status import build_status_report
from .storage import RagStore


def result_to_dict(result: SearchResult) -> dict[str, Any]:
    return {
        "path": result.chunk.path,
        "chunk_index": result.chunk.chunk_index,
        "score": round(result.score, 6),
        "text": result.chunk.text,
    }


def build_ask_response(
    store: RagStore,
    question: str,
    llm: str | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    started = time.perf_counter()
    results = search(store, question, top_k=top_k)
    retrieval_ms = round((time.perf_counter() - started) * 1000, 2)
    relevant = relevant_results(results)

    response: dict[str, Any] = {
        "question": question,
        "llm": llm,
        "timings": {"retrieval_ms": retrieval_ms},
        "sources": [result_to_dict(result) for result in results],
    }

    if llm and relevant:
        generation_started = time.perf_counter()
        try:
            response["answer"] = synthesize(question, relevant, provider=llm)
        except LlmError as error:
            response["error"] = str(error)
            response["answer"] = answer_from_results(question, results)
        response["timings"]["generation_ms"] = round(
            (time.perf_counter() - generation_started) * 1000, 2
        )
    else:
        response["answer"] = answer_from_results(question, results)
        response["timings"]["generation_ms"] = 0

    response["debug"] = {
        "retrieved_chunks": len(results),
        "relevant_chunks": len(relevant),
        "note": "Debug data shows retrieval steps, scores, sources, and timings, not hidden model reasoning.",
    }
    return response


class RagApiHandler(BaseHTTPRequestHandler):
    db_path = Path("storage/rag.sqlite3")
    static_dir = Path(__file__).parent / "static"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/":
            self._send_file(self.static_dir / "index.html")
            return
        if self.path.startswith("/static/"):
            requested = self.path.removeprefix("/static/").split("?", 1)[0]
            self._send_file(self.static_dir / requested)
            return
        if self.path == "/health":
            self._send_json({"ok": True})
            return
        if self.path == "/status":
            with RagStore(self.db_path) as store:
                report = build_status_report(store, self.db_path)
            self._send_json({"status": report})
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        try:
            if self.path == "/ask":
                payload = self._read_json_or_error()
                if payload is None:
                    return
                question = str(payload.get("question", "")).strip()
                if not question:
                    self._send_json({"error": "Missing question"}, status=400)
                    return
                with RagStore(self.db_path) as store:
                    response = build_ask_response(
                        store,
                        question=question,
                        llm=payload.get("llm"),
                        top_k=int(payload.get("top_k", 5)),
                    )
                self._send_json(response)
                return

            if self.path == "/ask/stream":
                self._stream_ask()
                return

            self._send_json({"error": "Not found"}, status=404)
        except Exception as error:
            self._send_json({"error": f"Internal server error: {error}"}, status=500)

    def _stream_ask(self) -> None:
        payload = self._read_json_or_error()
        if payload is None:
            return
        question = str(payload.get("question", "")).strip()
        llm = payload.get("llm", "ollama")
        top_k = int(payload.get("top_k", 5))

        if not question:
            self._send_json({"error": "Missing question"}, status=400)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        started = time.perf_counter()
        self._send_event("status", {"message": "retrieving context"})
        with RagStore(self.db_path) as store:
            results = search(store, question, top_k=top_k)
        relevant = relevant_results(results)
        self._send_event(
            "retrieval",
            {
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                "retrieved_chunks": len(results),
                "relevant_chunks": len(relevant),
                "sources": [result_to_dict(result) for result in results],
            },
        )

        if not llm or not relevant:
            self._send_event("answer", {"text": answer_from_results(question, results)})
            self._send_event("done", {"ok": True})
            return

        if llm != "ollama":
            self._send_event("status", {"message": f"using {llm} without token streaming"})
            try:
                answer = synthesize(question, relevant, provider=llm)
            except LlmError as error:
                self._send_event("error", {"message": str(error)})
            else:
                self._send_event("answer", {"text": answer})
            self._send_event("done", {"ok": True})
            return

        self._send_event(
            "status",
            {
                "message": "streaming answer from Ollama",
                "note": "Events expose progress, sources, and output tokens, not hidden model reasoning.",
            },
        )
        try:
            for token in stream_with_ollama(question, relevant):
                self._send_event("token", {"text": token})
        except LlmError as error:
            self._send_event("error", {"message": str(error)})
        self._send_event("done", {"ok": True})

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def _read_json_or_error(self) -> dict[str, Any] | None:
        try:
            payload = self._read_json()
        except json.JSONDecodeError as error:
            self._send_json({"error": f"Invalid JSON: {error.msg}"}, status=400)
            return None
        if not isinstance(payload, dict):
            self._send_json({"error": "JSON body must be an object"}, status=400)
            return None
        return payload

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        try:
            resolved = path.resolve()
            static_root = self.static_dir.resolve()
            if static_root not in resolved.parents and resolved != static_root:
                self._send_json({"error": "Not found"}, status=404)
                return
            body = resolved.read_bytes()
        except FileNotFoundError:
            self._send_json({"error": "Not found"}, status=404)
            return

        content_type = mimetypes.guess_type(str(resolved))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_event(self, event: str, payload: dict[str, Any]) -> None:
        self.wfile.write(f"event: {event}\n".encode("utf-8"))
        self.wfile.write(f"data: {json.dumps(payload)}\n\n".encode("utf-8"))
        self.wfile.flush()


def serve(host: str, port: int, db_path: Path) -> None:
    handler = type("ConfiguredRagApiHandler", (RagApiHandler,), {"db_path": db_path})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"RAG Learning API listening on http://{host}:{port}")
    server.serve_forever()
