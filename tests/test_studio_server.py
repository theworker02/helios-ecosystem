"""Live local API integration tests without third-party HTTP frameworks."""
import json
import pathlib
import sys
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import pytest

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "core" / "helios-chatgpt" / "server"))
from studio_server import StudioHandler, STUDIO_PAGE


@pytest.fixture
def studio():
    server = ThreadingHTTPServer(("127.0.0.1", 0), StudioHandler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def request(method, path, payload=None, headers=None):
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
        body = json.dumps(payload) if payload is not None else None
        merged = {"Content-Type": "application/json", **(headers or {})}
        try:
            conn.request(method, path, body=body, headers=merged)
            reply = conn.getresponse()
            content = reply.read()
            if reply.getheader("Content-Type", "").startswith("application/json"):
                return reply.status, json.loads(content)
            return reply.status, content.decode("utf-8")
        finally:
            conn.close()

    try:
        yield server, request
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def test_studio_page_and_live_creation(studio):
    server, request = studio
    assert STUDIO_PAGE.exists()
    status, page = request("GET", "/")
    assert status == 200 and "Helios Forge Studio" in page
    status, health = request("GET", "/api/health")
    assert status == 200 and health["status"] == "ok"
    status, result = request("POST", "/api/new", {"name": "integration", "genre": "sandbox",
                                                 "seed": 5, "width": 14, "height": 10})
    assert status == 200
    world_id = result["world_id"]
    status, snapshot = request("GET", f"/api/world?world_id={world_id}")
    assert status == 200
    assert snapshot["view"]["hud"]["genre"] == "sandbox"
    assert snapshot["world"]["forge"]["width"] == 14
    status, play = request("POST", "/api/play", {"world_id": world_id, "action": "wait"})
    assert status == 200 and play["result"]["turn"] == 1
    status, exported = request("POST", "/api/export", {"world_id": world_id})
    assert status == 200 and "helios.forge/v1" in exported["result"]["json"]
    status, imported = request("POST", "/api/import",
                               {"world_id": world_id, "json": exported["result"]["json"]})
    assert status == 200 and imported["result"]["hud"]["turn"] == 1


def test_studio_rejects_cross_origin_and_bad_requests(studio):
    server, request = studio
    port = server.server_port
    status, error = request("POST", "/api/new", {"name": "bad"}, {"Origin": "https://malicious.example"})
    assert status == 403
    status, result = request("POST", "/api/new", {"name": "safe"},
                             {"Origin": f"http://127.0.0.1:{port}"})
    assert status == 200 and result["world_id"]
    status, bad = request("POST", "/api/new", {"name": "bad", "genre": "unrecognized"})
    assert status == 400
    status, missing = request("GET", "/api/nonexistent")
    assert status == 404
    status, missing_world = request("GET", "/api/world")
    assert status == 400
    status, large = request("POST", "/api/import", {"data": "x" * 510000})
    assert status == 413
