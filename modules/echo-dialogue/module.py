"""Echo Dialogue: Branching and agent-driven dialogue, relationship context, conversation memory, and dialogue events."""

MODULE_ID = "echo-dialogue"
MODULE_NAME = "Echo Dialogue"


def install(world):
    """Install module-owned state into a Helios world dictionary."""
    mods = world.setdefault("modules", {})
    state = mods.setdefault(MODULE_ID, {"enabled": True, "data": {}})
    state["enabled"] = True
    return state


def handle_event(world, event):
    """Reference event hook. Modules evolve independently behind this contract."""
    state = install(world)
    state.setdefault("events_seen", 0)
    state["events_seen"] += 1
    return {"module": MODULE_ID, "handled": True, "event": event.get("type") if isinstance(event, dict) else None}
