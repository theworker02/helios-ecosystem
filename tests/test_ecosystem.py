import json, pathlib, importlib.util
ROOT=pathlib.Path(__file__).parents[1]
def test_registry_matches_modules():
 data=json.loads((ROOT/"registry.json").read_text())
 assert len(data["modules"])==20
 for m in data["modules"]:
  base=ROOT/"modules"/m["id"]
  assert (base/"README.md").exists() and (base/"module.json").exists() and (base/"logo.svg").exists()
def test_core_present():
 assert (ROOT/"core/helios-chatgpt/server/engine.py").exists()
