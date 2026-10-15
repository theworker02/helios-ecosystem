from __future__ import annotations
import copy, json, uuid

class HeliosEngine:
    def __init__(self): self.worlds={}
    def create_world(self,name,description=""):
        wid=str(uuid.uuid4())[:8]
        world={"id":wid,"name":name,"description":description,"tick":0,"entities":{},"modules":{},"events":[],"rules":[],"agents":{},"state":{}}
        self.worlds[wid]=world; return copy.deepcopy(world)
    def get_world(self,wid): return copy.deepcopy(self.worlds[wid])
    def add_entity(self,wid,entity_id,components=None):
        w=self.worlds[wid]; w["entities"][entity_id]={"id":entity_id,"components":components or {}}; return copy.deepcopy(w["entities"][entity_id])
    def emit(self,wid,event_type,payload=None):
        w=self.worlds[wid]; e={"type":event_type,"payload":payload or {},"tick":w["tick"]}; w["events"].append(e); return copy.deepcopy(e)
    def tick(self,wid,steps=1): self.worlds[wid]["tick"]+=max(1,int(steps)); return self.get_world(wid)
    def export_world(self,wid): return json.dumps(self.worlds[wid],sort_keys=True)
    def import_world(self,payload):
        w=json.loads(payload); self.worlds[w["id"]]=w; return self.get_world(w["id"])
