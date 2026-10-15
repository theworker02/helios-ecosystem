"""Local desktop plugin manifest and actual MCP stdio smoke tests."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).parents[1]
PLUGIN=ROOT/"plugins"/"helios"

def test_desktop_plugin_package():
    manifest=json.loads((PLUGIN/"plugin.json").read_text())
    mcp=json.loads((PLUGIN/"mcp.json").read_text())
    marketplace=json.loads((ROOT/".agents/plugins/marketplace.json").read_text())
    assert manifest["name"] == "helios-game-engine"
    assert manifest["extensions"]["com.openai"]["onboardingSkill"] == "./skills/setup/SKILL.md"
    assert marketplace["plugins"][0]["source"]["path"] == "./plugins/helios"
    assert mcp["mcpServers"]["helios"]["type"] == "stdio"
    assert mcp["mcpServers"]["helios"]["args"][0].endswith("/runtime/mcp_server.py")
    assert (PLUGIN/"assets/helios-logo.svg").is_file()
    core=ROOT/"core/helios-chatgpt/server"
    for f in core.glob("*.py"):
        if f.name=="studio_server.py":continue
        assert (PLUGIN/"runtime"/f.name).read_bytes()==f.read_bytes(),f"Bundled {f.name} is stale"

def test_local_desktop_server():
    messages=[
        {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","clientInfo":{"name":"smoke","version":"1"},"capabilities":{}}},
        {"jsonrpc":"2.0","method":"notifications/initialized"},
        {"jsonrpc":"2.0","id":2,"method":"tools/list"}
    ]
    proc=subprocess.run([sys.executable,str(PLUGIN/"runtime/mcp_server.py")],
            cwd=PLUGIN/"runtime",input="\n".join(json.dumps(m) for m in messages)+"\n",
            text=True,capture_output=True,timeout=15)
    assert proc.returncode == 0,proc.stderr
    result=[json.loads(line) for line in proc.stdout.splitlines()]
    assert result[0]["result"]["serverInfo"]["name"] == "helios-game-engine"
    names={t["name"] for t in result[1]["result"]["tools"]}
    assert {"helios_create_world","helios_forge_new","helios_forge_play","helios_raycast_frame"} <= names

def test_build_plugin(tmp_path):
    output=subprocess.run([sys.executable,str(ROOT/"scripts/build_desktop_plugin.py")],
                          text=True,capture_output=True,timeout=15,cwd=ROOT)
    assert output.returncode == 0,output.stderr
    import zipfile
    with zipfile.ZipFile(ROOT/"dist/helios-desktop-plugin.zip") as z:
        names=z.namelist()
        assert "plugin.json" in names and "mcp.json" in names
        assert "runtime/engine.py" in names and "runtime/mcp_server.py" in names
        assert "skills/game-builder/SKILL.md" in names
