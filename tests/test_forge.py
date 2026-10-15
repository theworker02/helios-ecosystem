"""Contract, replayable behavior and MCP integration checks for Forge."""
import json
import pathlib
import sys
import pytest

SERVER = pathlib.Path(__file__).parents[1] / "core" / "helios-chatgpt" / "server"
sys.path.insert(0, str(SERVER))
from engine import HeliosEngine
from forge import ForgeStudio
from mcp_server import TOOLS, dispatch


@pytest.mark.parametrize("genre", ["roguelike", "topdown", "platformer", "sandbox"])
def test_seeded_project_round_trip(genre):
    first = ForgeStudio.create("test", genre, seed=42)
    second = ForgeStudio.create("test", genre, seed=42)
    assert first == second
    assert first["schema"] == "helios.forge/v1"
    assert ForgeStudio.import_project(ForgeStudio.export(first)) == first
    frame = ForgeStudio.render(first)
    assert "@" in frame["ascii"]
    assert len(frame["ascii"].splitlines()) == first["height"]


def test_grid_movement_wall_and_editor():
    game = ForgeStudio.create("editable", "sandbox", width=10, height=8)
    x, y = game["player"]["x"], game["player"]["y"]
    ForgeStudio.edit(game, x + 1, y, "#")
    blocked = ForgeStudio.play(game, "east")
    assert (game["player"]["x"], game["player"]["y"]) == (x, y)
    assert any(e["type"] == "movement.blocked" for e in blocked["events"])
    ForgeStudio.edit(game, x + 1, y, ".")
    ForgeStudio.play(game, "east")
    assert game["player"]["x"] == x + 1
    with pytest.raises(ValueError):
        ForgeStudio.edit(game, x + 1, y, "#")


def test_npc_goal_loot_actions_and_checkpoint():
    e = HeliosEngine(seed=11)
    w = e.create_world("forge", mode="forge")
    wid = w["id"]
    e.forge_new(wid, "starter", "sandbox", 3, 12, 8)
    game = e._forge(wid)
    x, y = game["player"]["x"], game["player"]["y"]
    e.forge_place(wid, "reward", "loot", x + 1, y, value=55)
    e.forge_place(wid, "win", "goal", x + 2, y)
    e.checkpoint(wid, "start")
    move = e.forge_play(wid, "east")
    assert any(ev["type"] == "loot.collected" for ev in move["events"])
    assert e.forge_render(wid)["hud"]["score"] == 55
    goal = e.forge_play(wid, "east")
    assert goal["completed"]
    assert e.forge_play(wid, "wait")["events"] == []
    e.restore_checkpoint(wid, "start")
    assert e.forge_render(wid)["hud"]["score"] == 0
    assert "forge.action" in e.export_replay(wid)


def test_enemy_combat_and_damage():
    game = ForgeStudio.create("fight", "sandbox", width=10, height=8)
    x, y = game["player"]["x"], game["player"]["y"]
    ForgeStudio.place(game, "enemy", "enemy", x + 1, y, hp=40)
    first = ForgeStudio.play(game, "east")
    assert first["events"][0]["type"] == "combat.player_hit"
    assert game["player"]["x"] == x
    ForgeStudio.play(game, "attack")
    assert not next(a for a in game["actors"] if a["id"] == "enemy")["active"]


def test_platformer_physics_and_finite_frames():
    game = ForgeStudio.create("jump", "platformer", width=20, height=12)
    initial_y = game["player"]["y"]
    jump = ForgeStudio.play(game, "jump", frames=3)
    assert any(e["type"] == "player.jumped" for e in jump["events"])
    assert game["player"]["y"] < initial_y
    ForgeStudio.play(game, "wait", frames=50)
    assert game["player"]["y"] <= initial_y
    with pytest.raises(ValueError):
        ForgeStudio.play(game, "right", frames=100000)


def test_untrusted_project_rejected_without_execute():
    game = ForgeStudio.create("safe", "sandbox", width=10, height=8)
    obj = json.loads(ForgeStudio.export(game))
    obj["tiles"][0] = "__import__('os').system('echo hi')"
    with pytest.raises(ValueError):
        ForgeStudio.import_project(json.dumps(obj))
    with pytest.raises(ValueError):
        ForgeStudio.import_project(json.dumps({"schema": "helios.forge/v1"}))
    with pytest.raises(ValueError):
        ForgeStudio.import_project("x" * 500001)


def test_mcp_exposes_game_authoring_and_play():
    names = {t["name"] for t in TOOLS}
    assert {"helios_forge_new", "helios_forge_edit", "helios_forge_place",
            "helios_forge_play", "helios_forge_render",
            "helios_forge_export", "helios_forge_import"} <= names
    created = dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                        "params": {"name": "helios_create_world",
                                   "arguments": {"name": "MCP"}}})
    world = json.loads(created["result"]["content"][0]["text"])
    result = dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                       "params": {"name": "helios_forge_new",
                                  "arguments": {"world_id": world["id"], "name": "Studio",
                                                "genre": "sandbox"}}})
    rendered = json.loads(result["result"]["content"][0]["text"])
    assert rendered["hud"]["genre"] == "sandbox"
    assert "@" in rendered["ascii"]


def test_agent_forge_capability_gate():
    e = HeliosEngine()
    world = e.create_world("actor")
    wid = world["id"]
    e.forge_new(wid, "safe", "sandbox")
    e.spawn_entity(wid, "bot", {"transform": {"x": 1, "y": 1}})
    e.attach_agent(wid, "forbidden", "bot", ["inspect"])
    with pytest.raises(PermissionError):
        e.agent_act(wid, "forbidden", {"type": "forge", "command": "north"})
    e.attach_agent(wid, "permitted", "bot", ["forge"])
    assert e.agent_act(wid, "permitted", {"type": "forge", "command": "wait"})["accepted"]
