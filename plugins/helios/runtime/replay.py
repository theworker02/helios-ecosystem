from __future__ import annotations
import copy, json

class ReplayLog:
    def __init__(self, items=None):
        self.items=list(items or [])

    def record(self, tick, kind, payload):
        self.items.append({"tick":int(tick),"kind":str(kind),"payload":copy.deepcopy(payload)})
        return self.items[-1]

    def export(self):
        return json.dumps({"schema":"helios.replay/v1","items":self.items},sort_keys=True,separators=(",",":"))

    @classmethod
    def load(cls, payload):
        data=json.loads(payload)
        if data.get("schema")!="helios.replay/v1" or not isinstance(data.get("items"),list):
            raise ValueError("invalid Helios replay")
        return cls(data["items"])
