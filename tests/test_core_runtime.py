import pathlib, sys
SERVER=pathlib.Path(__file__).parents[1]/"core"/"helios-chatgpt"/"server"
sys.path.insert(0,str(SERVER))
from engine import HeliosEngine, ENGINE_VERSION

MAP="""#######
#.....#
#.P...#
#.....#
#######
"""

def test_world_entity_scene_and_save():
    e=HeliosEngine()
    w=e.create_world("test")
    assert w["engine_version"]=="1.4.0"
    e.spawn_entity(w["id"],"crate",{"transform":{"x":2,"y":2}},["prop"])
    assert e.query_entities(w["id"],component="transform")[0]["id"]=="crate"
    e.checkpoint(w["id"],"a")
    payload=e.export_world(w["id"])
    assert '"engine_version":"1.4.0"' in payload

def test_retro_fps_tick_and_frame():
    e=HeliosEngine(); w=e.create_world("fps",mode="retro_fps")
    e.configure_retro_fps(w["id"],MAP)
    e.apply_input(w["id"],"player",{"forward":1})
    e.tick(w["id"],2)
    frame=e.raycast_frame(w["id"],32,16)
    assert len(frame["rays"])==32
    assert len(frame["ascii"].splitlines())==16

def test_agent_capability_gate():
    e=HeliosEngine(); w=e.create_world("agents")
    e.spawn_entity(w["id"],"npc",{"transform":{"x":0,"y":0}})
    e.attach_agent(w["id"],"bot","npc",["inspect"])
    obs=e.observe_agent(w["id"],"bot")
    assert obs["self"]=="npc"
    try:
        e.agent_act(w["id"],"bot",{"type":"attack"})
        assert False
    except PermissionError:
        pass
