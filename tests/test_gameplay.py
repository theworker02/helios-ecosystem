import pathlib,sys
SERVER=pathlib.Path(__file__).parents[1]/"core"/"helios-chatgpt"/"server"
sys.path.insert(0,str(SERVER))
from engine import HeliosEngine

MAP="""########
#P.A.E.#
#..D...#
#..+...#
########
"""

def test_gameplay_spawn_fire_hud_and_door():
    e=HeliosEngine(seed=7); w=e.create_world("g",mode="retro_fps")
    summary=e.configure_retro_fps(w["id"],MAP)
    assert summary["spawns"]["enemy"]==1
    hud=e.hud(w["id"]); assert hud["health"]==100 and hud["ammo"]>=1
    before=hud["ammo"]; result=e.fire_weapon(w["id"])
    assert e.hud(w["id"])["ammo"]==before-1
    p=e._world(w["id"])["entities"]["player"]["components"]["transform"]
    p.update({"x":3.5,"y":1.5,"angle":1.57079632679})
    inter=e.interact(w["id"]); assert inter["changed"] is True

def test_replay_export():
    e=HeliosEngine(seed=1); w=e.create_world("r")
    e.tick(w["id"],2)
    payload=e.export_replay(w["id"])
    assert "helios.replay/v1" in payload
