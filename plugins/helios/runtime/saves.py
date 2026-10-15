from __future__ import annotations
import copy, json

class SaveStore:
    def __init__(self):
        self.checkpoints = {}

    def create(self, world, name):
        self.checkpoints.setdefault(world["id"], {})[name] = copy.deepcopy(world)
        return {"world_id":world["id"],"name":name,"tick":world["tick"]}

    def restore(self, world_id, name):
        return copy.deepcopy(self.checkpoints[world_id][name])

    @staticmethod
    def dumps(world):
        return json.dumps(world, sort_keys=True, separators=(",",":"))

    @staticmethod
    def loads(payload):
        data = json.loads(payload)
        if not isinstance(data, dict) or "id" not in data or "engine_version" not in data:
            raise ValueError("invalid Helios save")
        return data
