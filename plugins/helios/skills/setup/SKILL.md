---
name: setup
description: Configure and verify the local Helios MCP server in ChatGPT Desktop.
---

# Helios local MCP setup

Helios requires local MCP desktop plugin support and Python 3.10 or later.

1. Verify a supported interpreter with `python --version`. macOS installations may need `python3`, while some Windows machines use `py`.
2. The packaged `mcp.json` uses command `python` and launches the bundled `runtime/mcp_server.py`. If needed, change `command` to `python3` or `py` in the local installed manifest; for `py`, prepend `-3` to the `args`.
3. Verify the available tools include `helios_create_world`, `helios_forge_new`, `helios_forge_render`, and `helios_forge_play`.
4. Smoke test: create a Forge sandbox world, render it and advance one wait turn.
5. Tell users worlds are kept in-process and must be exported before the plugin's local MCP process terminates. Never pretend this local plugin is a public directory release or a hosted MCP endpoint.
