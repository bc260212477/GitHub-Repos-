#!/usr/bin/env python3
"""Small dependency-free HTTP API for the agent architecture builder."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from agent_architect import DEFAULT_CATALOG, load_repositories, recommend, search_repositories


def public_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        "name": row.get("name", ""),
        "full_name": row.get("full_name", ""),
        "url": row.get("url", ""),
        "description": row.get("description", ""),
        "stars": int(row.get("stars", "0") or 0),
        "license": row.get("license_spdx") or row.get("license_status") or "unknown",
        "category": row.get("category", ""),
    }


def create_handler(rows: list[dict[str, str]]) -> type[BaseHTTPRequestHandler]:
    class AgentAPIHandler(BaseHTTPRequestHandler):
        def _send(self, status: int, payload: Any) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._send(200, {"status": "ok", "repositories": len(rows)})
                return
            if parsed.path == "/api/repositories":
                params = parse_qs(parsed.query)
                query = params.get("q", [""])[0]
                try:
                    limit = min(max(int(params.get("limit", ["20"])[0]), 1), 100)
                except ValueError:
                    self._send(400, {"error": "limit must be an integer"})
                    return
                self._send(200, {"results": [public_row(row) for row in search_repositories(rows, query, limit)]})
                return
            self._send(404, {"error": "not found"})

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/api/architecture":
                self._send(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                product = str(payload.get("product", "")).strip()
                limit = int(payload.get("per_capability", 2))
                if not product or limit < 1 or limit > 10:
                    raise ValueError
            except (ValueError, TypeError, json.JSONDecodeError):
                self._send(400, {"error": "send product and per_capability (1-10)"})
                return
            result = recommend(rows, product.lower(), limit)
            self._send(200, {
                "product": product,
                "capabilities": {
                    capability: [public_row(row) for row in candidates]
                    for capability, candidates in result.items()
                },
            })

        def log_message(self, *_args: Any) -> None:
            return

    return AgentAPIHandler


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the agent architecture catalog API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    rows = load_repositories(args.catalog)
    server = ThreadingHTTPServer((args.host, args.port), create_handler(rows))
    print(f"Agent API listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
