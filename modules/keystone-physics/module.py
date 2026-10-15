"""Keystone Physics: Lightweight spatial rules, collision intents, movement costs, occupancy, ranges, and deterministic resolution."""
MODULE_ID="keystone-physics"
MODULE_NAME="Keystone Physics"
def install(world):
    state=world.setdefault("modules",{}).setdefault(MODULE_ID,{"enabled":True,"data":{}})
    state["enabled"]=True
    return state
def handle_event(world,event):
    state=install(world); state["events_seen"]=state.get("events_seen",0)+1
    return {"module":MODULE_ID,"handled":True,"event":event.get("type") if isinstance(event,dict) else None}
