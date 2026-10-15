from __future__ import annotations
import copy

class EntityStore:
    def __init__(self, data=None):
        self._entities = copy.deepcopy(data or {})

    def spawn(self, entity_id, components=None, tags=None):
        if not entity_id or entity_id in self._entities:
            raise ValueError("entity_id must be unique and non-empty")
        self._entities[entity_id] = {
            "id": entity_id,
            "components": copy.deepcopy(components or {}),
            "tags": sorted(set(tags or [])),
            "active": True,
        }
        return copy.deepcopy(self._entities[entity_id])

    def remove(self, entity_id):
        return self._entities.pop(entity_id, None) is not None

    def get(self, entity_id):
        if entity_id not in self._entities:
            raise KeyError(entity_id)
        return copy.deepcopy(self._entities[entity_id])

    def patch_component(self, entity_id, component, patch):
        e = self._entities[entity_id]
        current = e["components"].setdefault(component, {})
        if isinstance(current, dict) and isinstance(patch, dict):
            current.update(copy.deepcopy(patch))
        else:
            e["components"][component] = copy.deepcopy(patch)
        return copy.deepcopy(e)

    def query(self, component=None, tag=None, active_only=True):
        out = []
        for e in self._entities.values():
            if active_only and not e.get("active", True):
                continue
            if component and component not in e.get("components", {}):
                continue
            if tag and tag not in e.get("tags", []):
                continue
            out.append(copy.deepcopy(e))
        return out

    def raw(self):
        return self._entities

    def export(self):
        return copy.deepcopy(self._entities)
