from __future__ import annotations
import copy, math

DEFAULT_ACTIONS = {"move","turn","speak","inspect","use","attack","interact","wait"}

class AgentRuntime:
    def attach(self, world, agent_id, entity_id, capabilities=None, goals=None):
        if entity_id not in world["entities"]:
            raise KeyError(entity_id)
        world["agents"][agent_id] = {
            "id": agent_id,
            "entity_id": entity_id,
            "capabilities": sorted(set(capabilities or DEFAULT_ACTIONS)),
            "goals": list(goals or []),
            "memory": [],
        }
        return copy.deepcopy(world["agents"][agent_id])

    def observe(self, world, agent_id, radius=8.0):
        a = world["agents"][agent_id]
        origin = world["entities"][a["entity_id"]].get("components",{}).get("transform",{})
        ox, oy = float(origin.get("x",0)), float(origin.get("y",0))
        visible = []
        for e in world["entities"].values():
            t = e.get("components",{}).get("transform",{})
            if "x" not in t or "y" not in t:
                continue
            if math.hypot(float(t["x"])-ox, float(t["y"])-oy) <= radius:
                visible.append(copy.deepcopy(e))
        return {"tick":world["tick"],"self":a["entity_id"],"entities":visible,"recent_events":copy.deepcopy(world["events"][-16:])}

    def validate_action(self, world, agent_id, action):
        a = world["agents"][agent_id]
        typ = action.get("type")
        if typ not in a["capabilities"]:
            raise PermissionError(f"agent capability denied: {typ}")
        return True
