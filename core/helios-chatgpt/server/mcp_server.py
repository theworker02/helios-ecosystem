"""Helios 1.3.8 MCP stdio server."""
from __future__ import annotations
import json, os, sys
from engine import HeliosEngine, ENGINE_VERSION
from wad import WadFile

engine = HeliosEngine()

def obj(properties=None, required=None):
    return {"type":"object","properties":properties or {},"required":required or [],"additionalProperties":False}

S={"type":"string"}; N={"type":"number"}; I={"type":"integer"}; O={"type":"object"}; A={"type":"array"}

TOOLS=[
 {"name":"helios_create_world","description":"Create a Helios game/simulation world.","inputSchema":obj({"name":S,"description":S,"mode":S},["name"])},
 {"name":"helios_get_world","description":"Read authoritative world state.","inputSchema":obj({"world_id":S},["world_id"])},
 {"name":"helios_create_scene","description":"Create a scene.","inputSchema":obj({"world_id":S,"scene_id":S,"name":S,"metadata":O},["world_id","scene_id"])},
 {"name":"helios_spawn_entity","description":"Spawn an entity with components and tags.","inputSchema":obj({"world_id":S,"entity_id":S,"components":O,"tags":A,"scene_id":S},["world_id","entity_id"])},
 {"name":"helios_patch_component","description":"Patch one entity component.","inputSchema":obj({"world_id":S,"entity_id":S,"component":S,"patch":O},["world_id","entity_id","component","patch"])},
 {"name":"helios_query_entities","description":"Query entities by component or tag.","inputSchema":obj({"world_id":S,"component":S,"tag":S},["world_id"])},
 {"name":"helios_install_module","description":"Enable a Helios module for a world.","inputSchema":obj({"world_id":S,"module_id":S,"config":O},["world_id","module_id"])},
 {"name":"helios_add_rule","description":"Add a structured deterministic world rule.","inputSchema":obj({"world_id":S,"rule":O},["world_id","rule"])},
 {"name":"helios_configure_retro_fps","description":"Configure a Doom-style grid/raycast FPS from text map data. Does not use proprietary Doom assets.","inputSchema":obj({"world_id":S,"map_text":S,"player_entity":S,"fov_degrees":N},["world_id","map_text"])},
 {"name":"helios_apply_input","description":"Set bounded input state for an entity.","inputSchema":obj({"world_id":S,"entity_id":S,"input":O},["world_id","entity_id","input"])},
 {"name":"helios_tick","description":"Advance deterministic simulation steps.","inputSchema":obj({"world_id":S,"steps":I,"dt":N},["world_id"])},
 {"name":"helios_raycast_frame","description":"Render a retro-FPS raycast frame with ASCII output and ray distances.","inputSchema":obj({"world_id":S,"rays":I,"height":I},["world_id"])},
 {"name":"helios_attach_agent","description":"Attach a capability-gated AI agent to an entity.","inputSchema":obj({"world_id":S,"agent_id":S,"entity_id":S,"capabilities":A,"goals":A},["world_id","agent_id","entity_id"])},
 {"name":"helios_agent_observe","description":"Return bounded local observations for an attached agent.","inputSchema":obj({"world_id":S,"agent_id":S,"radius":N},["world_id","agent_id"])},
 {"name":"helios_agent_act","description":"Submit an action through the attached agent capability gate.","inputSchema":obj({"world_id":S,"agent_id":S,"action":O},["world_id","agent_id","action"])},
 {"name":"helios_checkpoint","description":"Create an in-memory world checkpoint.","inputSchema":obj({"world_id":S,"name":S},["world_id","name"])},
 {"name":"helios_restore_checkpoint","description":"Restore an in-memory checkpoint.","inputSchema":obj({"world_id":S,"name":S},["world_id","name"])},
 {"name":"helios_export_world","description":"Export a portable Helios save as JSON.","inputSchema":obj({"world_id":S},["world_id"])},
 {"name":"helios_import_world","description":"Import a portable Helios save JSON.","inputSchema":obj({"json":S},["json"])},
 {"name":"helios_inspect_wad","description":"Inspect a local user-supplied classic Doom IWAD/PWAD and list maps. The plugin never supplies copyrighted WAD content.","inputSchema":obj({"path":S,"map_name":S},["path"])}
]

def ok(i,r): return {"jsonrpc":"2.0","id":i,"result":r}
def tool(payload,error=False): return {"content":[{"type":"text","text":json.dumps(payload,ensure_ascii=False,default=str)}],"isError":error}

def dispatch(q):
    i=q.get("id"); m=q.get("method")
    if m=="initialize":
        return ok(i,{"protocolVersion":"2025-03-26","capabilities":{"tools":{"listChanged":False}},"serverInfo":{"name":"helios-game-engine","version":ENGINE_VERSION}})
    if m in ("notifications/initialized","notifications/cancelled"): return None
    if m=="ping": return ok(i,{})
    if m=="tools/list": return ok(i,{"tools":TOOLS})
    if m!="tools/call":
        return {"jsonrpc":"2.0","id":i,"error":{"code":-32601,"message":"Method not found"}}
    p=q.get("params") or {}; n=p.get("name"); a=p.get("arguments") or {}
    try:
        if n=="helios_create_world": r=engine.create_world(a["name"],a.get("description",""),a.get("mode","simulation"))
        elif n=="helios_get_world": r=engine.get_world(a["world_id"])
        elif n=="helios_create_scene": r=engine.create_scene(a["world_id"],a["scene_id"],a.get("name"),a.get("metadata"))
        elif n=="helios_spawn_entity": r=engine.spawn_entity(a["world_id"],a["entity_id"],a.get("components"),a.get("tags"),a.get("scene_id"))
        elif n=="helios_patch_component": r=engine.patch_component(a["world_id"],a["entity_id"],a["component"],a["patch"])
        elif n=="helios_query_entities": r=engine.query_entities(a["world_id"],a.get("component"),a.get("tag"))
        elif n=="helios_install_module": r=engine.install_module(a["world_id"],a["module_id"],a.get("config"))
        elif n=="helios_add_rule": r=engine.add_rule(a["world_id"],a["rule"])
        elif n=="helios_configure_retro_fps": r=engine.configure_retro_fps(a["world_id"],a["map_text"],a.get("player_entity","player"),a.get("fov_degrees",60))
        elif n=="helios_apply_input": r=engine.apply_input(a["world_id"],a["entity_id"],a["input"])
        elif n=="helios_tick": r=engine.tick(a["world_id"],a.get("steps",1),a.get("dt"))
        elif n=="helios_raycast_frame": r=engine.raycast_frame(a["world_id"],a.get("rays",80),a.get("height",24))
        elif n=="helios_attach_agent": r=engine.attach_agent(a["world_id"],a["agent_id"],a["entity_id"],a.get("capabilities"),a.get("goals"))
        elif n=="helios_agent_observe": r=engine.observe_agent(a["world_id"],a["agent_id"],a.get("radius",8))
        elif n=="helios_agent_act": r=engine.agent_act(a["world_id"],a["agent_id"],a["action"])
        elif n=="helios_checkpoint": r=engine.checkpoint(a["world_id"],a["name"])
        elif n=="helios_restore_checkpoint": r=engine.restore_checkpoint(a["world_id"],a["name"])
        elif n=="helios_export_world": r={"json":engine.export_world(a["world_id"])}
        elif n=="helios_import_world": r=engine.import_world(a["json"])
        elif n=="helios_inspect_wad":
            wad=WadFile(os.path.abspath(a["path"])); r=wad.map_geometry(a["map_name"]) if a.get("map_name") else wad.summary()
        else: raise ValueError("unknown tool")
        return ok(i,tool(r))
    except (ValueError,KeyError,TypeError,PermissionError,OSError) as e:
        return ok(i,tool({"error":str(e),"type":type(e).__name__},True))

def main():
    for line in sys.stdin:
        try:
            req=json.loads(line)
            res=dispatch(req)
            if res is not None: print(json.dumps(res,ensure_ascii=False),flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":"Parse error"}}),flush=True)

if __name__=="__main__": main()
