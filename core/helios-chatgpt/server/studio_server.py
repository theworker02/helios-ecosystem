"""Loopback-only HTTP bridge for the Helios Forge browser studio.

Not intended as an internet-facing service. Deploy behind independently
implemented authorization, isolation, TLS, quotas and persistent storage.
"""
from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from engine import HeliosEngine

MAX_BYTES = 500_000
STUDIO_PAGE = Path(__file__).parents[3] / "studio" / "index.html"


class StudioHandler(BaseHTTPRequestHandler):
    engine = HeliosEngine()
    lock = threading.RLock()

    def _reply(self, code, payload, content_type="application/json; charset=utf-8"):
        body = (json.dumps(payload, ensure_ascii=False).encode("utf-8")
                if not isinstance(payload, bytes) else payload)
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def _local_origin(self):
        origin = self.headers.get("Origin")
        if origin is None:
            return True
        try:
            parsed = urlparse(origin)
            return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"} and parsed.port == self.server.server_address[1]
        except ValueError:
            return False

    def do_GET(self):
        url = urlparse(self.path)
        try:
            if url.path in {"/", "/index.html"}:
                self._reply(200, STUDIO_PAGE.read_bytes(), "text/html; charset=utf-8")
            elif url.path == "/api/world":
                wid = parse_qs(url.query).get("world_id", [None])[0]
                if not wid:
                    raise ValueError("world_id is required")
                with self.lock:
                    result = {"world": self.engine.get_world(wid),
                              "view": self.engine.forge_render(wid)}
                self._reply(200, result)
            elif url.path == "/api/health":
                self._reply(200, {"status": "ok", "service": "helios-studio"})
            else:
                self._reply(404, {"error": "not found"})
        except (ValueError, KeyError) as exc:
            self._reply(400, {"error": str(exc)})

    def do_POST(self):
        if not self._local_origin():
            self._reply(403, {"error": "cross-origin request forbidden"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > MAX_BYTES:
                self._reply(413, {"error": "request body too large or empty"})
                return
            data = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("expected JSON object")
            url = urlparse(self.path).path
            with self.lock:
                if url == "/api/new":
                    world = self.engine.create_world(data.get("name", "Untitled"), mode="forge")
                    wid = world["id"]
                    view = self.engine.forge_new(wid, data.get("name", "Untitled"),
                              data.get("genre", "roguelike"), data.get("seed", 0),
                              data.get("width", 24), data.get("height", 16))
                    output = {"world_id": wid, "view": view}
                else:
                    wid = data["world_id"]
                    if url == "/api/edit":
                        output = self.engine.forge_edit(wid, data["x"], data["y"], data["tile"])
                    elif url == "/api/place":
                        output = self.engine.forge_place(wid, data["actor_id"], data["kind"], data["x"], data["y"],
                                    data.get("hp", 35), data.get("value", 10), data.get("dialogue", ""))
                    elif url == "/api/play":
                        output = self.engine.forge_play(wid, data["action"], data.get("frames", 1))
                    elif url == "/api/export":
                        output = {"json": self.engine.forge_export(wid)}
                    elif url == "/api/import":
                        output = self.engine.forge_import(wid, data["json"])
                    else:
                        self._reply(404, {"error": "not found"})
                        return
            self._reply(200, {"result": output})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, OverflowError) as exc:
            self._reply(400, {"error": str(exc)})

    def log_message(self, fmt, *args):
        if os.environ.get("HELIOS_STUDIO_DEBUG") == "1":
            super().log_message(fmt, *args)


def main():
    host = "127.0.0.1"
    port = int(os.environ.get("HELIOS_STUDIO_PORT", "8787"))
    if not 1 <= port <= 65535:
        raise ValueError("invalid HTTP port")
    with ThreadingHTTPServer((host, port), StudioHandler) as server:
        print(f"Helios Forge Studio at http://{host}:{port}", flush=True)
        server.serve_forever(poll_interval=0.1)


if __name__ == "__main__":
    main()
