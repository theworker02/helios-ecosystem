"""Shared Helios module contract helpers."""
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class HeliosModule:
    module_id: str
    name: str
    version: str = "0.1.0"
    capabilities: list[str] = field(default_factory=list)
    on_event: Callable[[dict, dict], Any] | None = None

def emit(world: dict, event_type: str, payload: dict | None = None) -> dict:
    event={"type":event_type,"payload":payload or {}}
    world.setdefault("events",[]).append(event)
    return event
