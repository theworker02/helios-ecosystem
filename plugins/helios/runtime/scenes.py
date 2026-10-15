from __future__ import annotations
import copy

class SceneStore:
    def __init__(self, scenes=None, active=None):
        self.scenes = copy.deepcopy(scenes or {})
        self.active = active

    def create(self, scene_id, name=None, metadata=None):
        if scene_id in self.scenes:
            raise ValueError("scene already exists")
        self.scenes[scene_id] = {
            "id": scene_id,
            "name": name or scene_id,
            "metadata": copy.deepcopy(metadata or {}),
            "entities": [],
        }
        if self.active is None:
            self.active = scene_id
        return copy.deepcopy(self.scenes[scene_id])

    def set_active(self, scene_id):
        if scene_id not in self.scenes:
            raise KeyError(scene_id)
        self.active = scene_id
        return scene_id

    def add_entity(self, scene_id, entity_id):
        scene = self.scenes[scene_id]
        if entity_id not in scene["entities"]:
            scene["entities"].append(entity_id)

    def export(self):
        return {"active": self.active, "items": copy.deepcopy(self.scenes)}
