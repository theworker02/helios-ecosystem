#!/usr/bin/env python3
"""Build a self-contained Helios desktop plugin ZIP from bundled runtime."""
import argparse
import filecmp
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "helios"
CORE = ROOT / "core" / "helios-chatgpt" / "server"
RUNTIME = PLUGIN / "runtime"
EXCLUDED = {"studio_server.py"}

def validate(sync=False):
    RUNTIME.mkdir(parents=True, exist_ok=True)
    expected = {p.name for p in CORE.glob("*.py") if p.name not in EXCLUDED}
    for name in expected:
        src, dest = CORE/name, RUNTIME/name
        if sync:
            shutil.copyfile(src, dest)
        if not dest.exists() or not filecmp.cmp(src, dest, shallow=False):
            raise RuntimeError(f"Outdated bundled server: {name} (rerun --sync)")
    if {p.name for p in RUNTIME.glob("*.py")} - expected:
        raise RuntimeError("Unexpected files in plugin runtime")
    plugin = json.loads((PLUGIN/"plugin.json").read_text())
    mcp = json.loads((PLUGIN/"mcp.json").read_text())
    assert plugin["name"] == "helios-game-engine"
    assert mcp["mcpServers"]["helios"]["type"] == "stdio"
    assert mcp["mcpServers"]["helios"]["args"][0].endswith("/runtime/mcp_server.py")
    assert (PLUGIN/"skills"/"setup"/"SKILL.md").is_file()
    return plugin

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync", action="store_true")
    options=parser.parse_args()
    plugin=validate(sync=options.sync)
    out=ROOT/"dist"/"helios-desktop-plugin.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(PLUGIN.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                archive.write(p,p.relative_to(PLUGIN).as_posix())
    print(f"Built {plugin['name']} {plugin['version']} at {out}")

if __name__ == "__main__":
    main()
