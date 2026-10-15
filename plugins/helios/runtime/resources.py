from __future__ import annotations
import copy, hashlib, json, os

class ResourcePack:
    def __init__(self, manifest):
        if manifest.get("schema")!="helios.resources/v1":
            raise ValueError("unsupported resource manifest")
        self.manifest=copy.deepcopy(manifest)

    @classmethod
    def from_json(cls, payload):
        return cls(json.loads(payload))

    def summary(self):
        assets=self.manifest.get("assets",[])
        return {
            "id":self.manifest.get("id"),
            "name":self.manifest.get("name"),
            "version":self.manifest.get("version"),
            "asset_count":len(assets),
            "kinds":sorted(set(a.get("kind","unknown") for a in assets)),
        }

    @staticmethod
    def digest_bytes(data):
        return hashlib.sha256(data).hexdigest()
