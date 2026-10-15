# Installing Helios Game Studio in ChatGPT Desktop

Helios has a portable local plugin at `plugins/helios/` and a repository marketplace in `.agents/plugins/marketplace.json`. Unlike the original project MCP configuration, this plugin includes the complete Python engine in `plugins/helios/runtime/`, so its installed cached copy works without the source repository beside it.

## Desktop prerequisites

- A desktop client supporting **local MCP plugins** (not all surfaces or plans expose them).
- Python 3.10+ installed on the computer, accessible as `python` from your command line.
- An installation from the repository's plugin marketplace.

## Install

1. Clone `https://github.com/theworker02/helios-ecosystem` locally or open the repo in the desktop Codex workspace.
2. Open ChatGPT Desktop > Plugins; choose the **Magnexis Game Tools** repository marketplace. If not detected, in a terminal with Codex CLI installed run `codex plugin marketplace add theworker02/helios-ecosystem`, then restart the desktop app.
3. Install **Helios Game Studio** from the marketplace.
4. Open a new chat, optionally @mention the plugin, and ask: "Create a Helios sandbox game and show its map."
5. If local tools cannot start, run `python --version`. On macOS edit `plugins/helios/mcp.json` and change the command to `python3`, then refresh/reinstall. On Windows where `py` is the only launcher, use `"command":"py"` and add `"-3"` before the script path in `args`.

In a local development checkout, run `python scripts/build_desktop_plugin.py` to validate the bundled source and generate `dist/helios-desktop-plugin.zip` with the manifest at the ZIP root. Run `python scripts/build_desktop_plugin.py --sync` first after source-code changes to rebuild the Python snapshot. The ZIP is optional for marketplace installation.

Desktop-only plugins containing local MCP servers can be tested through local marketplaces; public directory submission requires partner allowlisting and review. This repository change does **not** create a public listing, an installed account plugin, or a ChatGPT in-chat graphical game panel.

The separate `studio/index.html` is an optional local browser game editor started by `python core/helios-chatgpt/server/studio_server.py`, available at `http://127.0.0.1:8787`. It is not an embedded ChatGPT UI widget.

For browser/mobile use, build and deploy an authenticated streamable-HTTP MCP server over HTTPS. Do not expose the localhost Studio bridge to the public internet.

**Local filesystem caution:** The bundled tool `helios_inspect_wad` reads a local file path supplied in its arguments. Avoid opening untrusted or sensitive paths.
