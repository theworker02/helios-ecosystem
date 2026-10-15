"""Minimal Helios MCP stdio server."""
from __future__ import annotations
import json, sys
from engine import HeliosEngine
engine=HeliosEngine()
TOOLS=[
 {"name":"create_world","description":"Create a persistent Helios world.","inputSchema":{"type":"object","properties":{"name":{"type":"string"},"description":{"type":"string"}},"required":["name"]}},
 {"name":"get_world","description":"Read authoritative world state.","inputSchema":{"type":"object","properties":{"world_id":{"type":"string"}},"required":["world_id"]}},
 {"name":"add_entity","description":"Add an entity with structured components.","inputSchema":{"type":"object","properties":{"world_id":{"type":"string"},"entity_id":{"type":"string"},"components":{"type":"object"}},"required":["world_id","entity_id"]}},
 {"name":"emit_event","description":"Emit a world event.","inputSchema":{"type":"object","properties":{"world_id":{"type":"string"},"type":{"type":"string"},"payload":{"type":"object"}},"required":["world_id","type"]}},
 {"name":"tick_world","description":"Advance the deterministic simulation clock.","inputSchema":{"type":"object","properties":{"world_id":{"type":"string"},"steps":{"type":"integer","minimum":1,"maximum":100}},"required":["world_id"]}},
 {"name":"export_world","description":"Export portable JSON world state.","inputSchema":{"type":"object","properties":{"world_id":{"type":"string"}},"required":["world_id"]}}
]
def ok(i,r): return {"jsonrpc":"2.0","id":i,"result":r}
def dispatch(q):
 i=q.get("id"); m=q.get("method"); p=q.get("params") or {}
 if m=="initialize": return ok(i,{"protocolVersion":"2025-03-26","capabilities":{"tools":{"listChanged":False}},"serverInfo":{"name":"helios","version":"0.1.0"}})
 if m=="tools/list": return ok(i,{"tools":TOOLS})
 if m=="tools/call":
  n=p.get("name"); a=p.get("arguments") or {}
  if n=="create_world": r=engine.create_world(a["name"],a.get("description",""))
  elif n=="get_world": r=engine.get_world(a["world_id"])
  elif n=="add_entity": r=engine.add_entity(a["world_id"],a["entity_id"],a.get("components"))
  elif n=="emit_event": r=engine.emit(a["world_id"],a["type"],a.get("payload"))
  elif n=="tick_world": r=engine.tick(a["world_id"],a.get("steps",1))
  elif n=="export_world": r={"json":engine.export_world(a["world_id"])}
  else: return {"jsonrpc":"2.0","id":i,"error":{"code":-32602,"message":"Unknown tool"}}
  return ok(i,{"content":[{"type":"text","text":json.dumps(r)}]})
 if m in ("notifications/initialized","notifications/cancelled"): return None
 if m=="ping": return ok(i,{})
 return {"jsonrpc":"2.0","id":i,"error":{"code":-32601,"message":"Method not found"}}
for line in sys.stdin:
 try:
  r=dispatch(json.loads(line));
  if r is not None: print(json.dumps(r),flush=True)
 except Exception as e: print(json.dumps({"jsonrpc":"2.0","id":None,"error":{"code":-32000,"message":str(e)}}),flush=True)
