from __future__ import annotations
import copy, math, uuid
from ecs import EntityStore
from events import EventBus
from scenes import SceneStore
from retro_fps import RetroMap, cast_rays, move, ascii_frame
from rules import evaluate, apply_effect
from agents import AgentRuntime
from saves import SaveStore
from rng import DeterministicRng
from replay import ReplayLog
from gameplay import GameplaySystem
from resources import ResourcePack

ENGINE_VERSION = "1.4.0"

class HeliosEngine:
    def __init__(self, seed=0):
        self.worlds={}
        self.saves=SaveStore()
        self.agents=AgentRuntime()
        self.rng=DeterministicRng(seed)
        self.gameplay=GameplaySystem(self.rng)
        self.replays={}

    def create_world(self,name,description="",mode="simulation"):
        wid=uuid.uuid4().hex[:12]
        w={"engine_version":ENGINE_VERSION,"id":wid,"name":name,"description":description,"mode":mode,
           "tick":0,"time":0.0,"fixed_dt":1/20,"entities":{},"scenes":{},"active_scene":None,
           "modules":{},"events":[],"rules":[],"agents":{},"state":{},"input":{},"retro_fps":None,
           "doors":{},"resources":[],"rng":self.rng.state()}
        self.worlds[wid]=w; self.replays[wid]=ReplayLog(); self.create_scene(wid,"main","Main")
        return self.get_world(wid)

    def _world(self,wid):
        if wid not in self.worlds: raise KeyError(f"unknown world: {wid}")
        return self.worlds[wid]
    def get_world(self,wid): return copy.deepcopy(self._world(wid))

    def create_scene(self,wid,scene_id,name=None,metadata=None):
        w=self._world(wid); ss=SceneStore(w["scenes"],w["active_scene"]); scene=ss.create(scene_id,name,metadata)
        w["scenes"]=ss.scenes; w["active_scene"]=ss.active; return scene
    def set_scene(self,wid,scene_id):
        w=self._world(wid)
        if scene_id not in w["scenes"]: raise KeyError(scene_id)
        w["active_scene"]=scene_id; return scene_id

    def spawn_entity(self,wid,entity_id,components=None,tags=None,scene_id=None):
        w=self._world(wid); store=EntityStore(w["entities"]); entity=store.spawn(entity_id,components,tags); w["entities"]=store.raw()
        sid=scene_id or w["active_scene"]
        if sid and entity_id not in w["scenes"][sid]["entities"]: w["scenes"][sid]["entities"].append(entity_id)
        self.emit(wid,"entity.spawned",{"entity_id":entity_id}); return entity
    def patch_component(self,wid,entity_id,component,patch):
        w=self._world(wid); store=EntityStore(w["entities"]); entity=store.patch_component(entity_id,component,patch); w["entities"]=store.raw()
        self.emit(wid,"entity.component_patched",{"entity_id":entity_id,"component":component}); return entity
    def query_entities(self,wid,component=None,tag=None): return EntityStore(self._world(wid)["entities"]).query(component,tag)

    def install_module(self,wid,module_id,config=None):
        w=self._world(wid); state=w["modules"].setdefault(module_id,{"enabled":True,"config":{},"state":{}})
        state["enabled"]=True; state["config"].update(copy.deepcopy(config or {})); self.emit(wid,"module.installed",{"module_id":module_id}); return copy.deepcopy(state)

    def mount_resources(self,wid,manifest_json):
        w=self._world(wid); pack=ResourcePack.from_json(manifest_json); summary=pack.summary(); w["resources"].append(summary)
        self.emit(wid,"resources.mounted",summary); return summary

    def add_rule(self,wid,rule):
        w=self._world(wid); r=copy.deepcopy(rule); r.setdefault("id",uuid.uuid4().hex[:8]); w["rules"].append(r); return copy.deepcopy(r)

    def emit(self,wid,event_type,payload=None,source="engine"):
        w=self._world(wid); bus=EventBus(w["events"]); e=bus.emit(event_type,payload,w["tick"],source); w["events"]=bus.history
        context={"world":w,"event":e}
        for rule in w["rules"]:
            if rule.get("enabled",True) and evaluate(rule,context):
                for effect in rule.get("effects",[]): apply_effect(effect,context)
        return e

    def configure_retro_fps(self,wid,map_text,player_entity="player",fov_degrees=60):
        w=self._world(wid); level=RetroMap.from_text(map_text); x,y=level.spawn()
        w["retro_fps"]={"map":level.rows,"fov":float(fov_degrees),"player":player_entity}
        if player_entity not in w["entities"]:
            self.spawn_entity(wid,player_entity,{"transform":{"x":x,"y":y,"angle":0.0},"player":{"health":100,"armor":0},"inventory":{"ammo":20,"weapon":"pistol"}},["player"])
        else: self.patch_component(wid,player_entity,"transform",{"x":x,"y":y,"angle":0.0})
        spawns=self.gameplay.configure_from_map(self,wid) or {}
        return {"map":copy.deepcopy(w["retro_fps"]["map"]),"fov":w["retro_fps"]["fov"],"player":player_entity,"spawns":spawns}

    def apply_input(self,wid,entity_id,input_state):
        w=self._world(wid); w["input"][entity_id]=copy.deepcopy(input_state)
        self.replays.setdefault(wid,ReplayLog()).record(w["tick"],"input",{"entity_id":entity_id,"input":copy.deepcopy(input_state)})
        return copy.deepcopy(w["input"][entity_id])

    def _dynamic_level(self,w):
        return self.gameplay._dynamic_level(w) if w.get("retro_fps") else None

    def _step_retro_player(self,w,entity_id,inp):
        cfg=w.get("retro_fps")
        if not cfg or cfg.get("player")!=entity_id:return
        ent=w["entities"][entity_id]; t=ent["components"].setdefault("transform",{"x":1.5,"y":1.5,"angle":0.0}); level=self._dynamic_level(w)
        speed=float(inp.get("speed",0.12)); turn_speed=float(inp.get("turn_speed",0.10))
        x,y,a=move(level,float(t["x"]),float(t["y"]),float(t.get("angle",0)),float(inp.get("forward",0))*speed,float(inp.get("strafe",0))*speed,float(inp.get("turn",0))*turn_speed)
        t.update({"x":x,"y":y,"angle":a})

    def tick(self,wid,steps=1,dt=None):
        w=self._world(wid); steps=max(1,min(int(steps),1000)); step_dt=float(dt if dt is not None else w["fixed_dt"])
        for _ in range(steps):
            for entity_id,inp in list(w["input"].items()):
                if entity_id in w["entities"]: self._step_retro_player(w,entity_id,inp)
            self.gameplay.update_pickups(self,wid); self.gameplay.update_enemies(self,wid)
            w["tick"]+=1; w["time"]+=step_dt; w["rng"]=self.rng.state(); self.emit(wid,"helios.tick",{"dt":step_dt})
        self.replays.setdefault(wid,ReplayLog()).record(w["tick"],"tick",{"steps":steps,"dt":step_dt})
        return self.get_world(wid)

    def raycast_frame(self,wid,rays=80,height=24):
        w=self._world(wid); cfg=w.get("retro_fps")
        if not cfg: raise ValueError("retro FPS is not configured")
        ent=w["entities"][cfg["player"]]; t=ent["components"]["transform"]; level=self._dynamic_level(w)
        cast=cast_rays(level,float(t["x"]),float(t["y"]),float(t.get("angle",0)),math.radians(cfg["fov"]),rays)
        return {"rays":cast,"ascii":ascii_frame(cast,height),"player":copy.deepcopy(t),"hud":self.hud(wid),"tick":w["tick"]}

    def fire_weapon(self,wid):
        w=self._world(wid); result=self.gameplay.fire(self,wid); self.replays.setdefault(wid,ReplayLog()).record(w["tick"],"fire",copy.deepcopy(result)); return result
    def interact(self,wid):
        w=self._world(wid); result=self.gameplay.interact(w); self.emit(wid,"player.interact",result); self.replays.setdefault(wid,ReplayLog()).record(w["tick"],"interact",copy.deepcopy(result)); return result
    def hud(self,wid): return self.gameplay.hud(self._world(wid))

    def attach_agent(self,wid,agent_id,entity_id,capabilities=None,goals=None):
        return self.agents.attach(self._world(wid),agent_id,entity_id,capabilities,goals)
    def observe_agent(self,wid,agent_id,radius=8): return self.agents.observe(self._world(wid),agent_id,float(radius))
    def agent_act(self,wid,agent_id,action):
        w=self._world(wid); self.agents.validate_action(w,agent_id,action); entity_id=w["agents"][agent_id]["entity_id"]; typ=action.get("type")
        if typ in ("move","turn"): self.apply_input(wid,entity_id,{"forward":action.get("forward",0),"strafe":action.get("strafe",0),"turn":action.get("turn",0)})
        elif typ=="attack" and entity_id==(w.get("retro_fps") or {}).get("player"): self.fire_weapon(wid)
        elif typ=="interact" and entity_id==(w.get("retro_fps") or {}).get("player"): self.interact(wid)
        self.emit(wid,"agent.action",{"agent_id":agent_id,"entity_id":entity_id,"action":copy.deepcopy(action)},source=agent_id)
        self.replays.setdefault(wid,ReplayLog()).record(w["tick"],"agent_action",{"agent_id":agent_id,"action":copy.deepcopy(action)})
        return {"accepted":True,"entity_id":entity_id,"action":copy.deepcopy(action)}

    def checkpoint(self,wid,name): return self.saves.create(self._world(wid),name)
    def restore_checkpoint(self,wid,name): self.worlds[wid]=self.saves.restore(wid,name); return self.get_world(wid)
    def export_world(self,wid): return self.saves.dumps(self._world(wid))
    def import_world(self,payload):
        w=self.saves.loads(payload); self.worlds[w["id"]]=w; self.replays[w["id"]]=ReplayLog(); return self.get_world(w["id"])
    def export_replay(self,wid): return self.replays.setdefault(wid,ReplayLog()).export()
