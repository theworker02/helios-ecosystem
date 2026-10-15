from __future__ import annotations
import copy, math
from pathfinding import astar, line_of_sight
from retro_fps import RetroMap

class GameplaySystem:
    def __init__(self, rng):
        self.rng=rng

    def hud(self, world):
        cfg=world.get("retro_fps") or {}
        pid=cfg.get("player")
        if not pid or pid not in world["entities"]:
            return {"health":None,"ammo":None,"weapon":None}
        c=world["entities"][pid]["components"]
        p=c.setdefault("player",{"health":100,"armor":0})
        inv=c.setdefault("inventory",{"ammo":20,"weapon":"pistol"})
        return {"health":p.get("health",100),"armor":p.get("armor",0),"ammo":inv.get("ammo",0),"weapon":inv.get("weapon","pistol"),"tick":world["tick"]}

    def configure_from_map(self, engine, world_id):
        w=engine._world(world_id); cfg=w.get("retro_fps")
        if not cfg: return
        rows=cfg["map"]; count={"enemy":0,"health":0,"ammo":0,"door":0}
        clean=[]
        for y,row in enumerate(rows):
            chars=list(row)
            for x,ch in enumerate(chars):
                if ch=="E":
                    eid=f"enemy_{count['enemy']}"; count["enemy"]+=1
                    engine.spawn_entity(world_id,eid,{
                        "transform":{"x":x+0.5,"y":y+0.5,"angle":0.0},
                        "enemy":{"health":40,"damage":5,"speed":0.05,"aggro_range":8.0},
                    },["enemy"])
                    chars[x]="."
                elif ch=="+":
                    eid=f"health_{count['health']}"; count["health"]+=1
                    engine.spawn_entity(world_id,eid,{"transform":{"x":x+0.5,"y":y+0.5},"pickup":{"kind":"health","amount":25}},["pickup"])
                    chars[x]="."
                elif ch=="A":
                    eid=f"ammo_{count['ammo']}"; count["ammo"]+=1
                    engine.spawn_entity(world_id,eid,{"transform":{"x":x+0.5,"y":y+0.5},"pickup":{"kind":"ammo","amount":10}},["pickup"])
                    chars[x]="."
                elif ch=="D":
                    did=f"{x},{y}"; count["door"]+=1
                    w.setdefault("doors",{})[did]={"x":x,"y":y,"open":False}
            clean.append("".join(chars))
        cfg["map"]=clean
        return count

    def _dynamic_level(self, world):
        cfg=world["retro_fps"]; rows=list(cfg["map"])
        for d in world.get("doors",{}).values():
            y,x=int(d["y"]),int(d["x"])
            row=list(rows[y]); row[x]="." if d.get("open") else "#"; rows[y]="".join(row)
        return RetroMap(rows)

    def interact(self, world):
        cfg=world.get("retro_fps")
        if not cfg: raise ValueError("retro FPS is not configured")
        p=world["entities"][cfg["player"]]["components"]["transform"]
        fx=p["x"]+math.cos(p.get("angle",0))*0.9
        fy=p["y"]+math.sin(p.get("angle",0))*0.9
        cx,cy=int(fx),int(fy)
        d=world.get("doors",{}).get(f"{cx},{cy}")
        if not d: return {"changed":False}
        d["open"]=not d.get("open",False)
        return {"changed":True,"door":copy.deepcopy(d)}

    def fire(self, engine, world_id, max_distance=12.0, damage=20):
        w=engine._world(world_id); cfg=w.get("retro_fps")
        if not cfg: raise ValueError("retro FPS is not configured")
        player=w["entities"][cfg["player"]]; pc=player["components"]
        inv=pc.setdefault("inventory",{"ammo":20,"weapon":"pistol"})
        if inv.get("ammo",0)<=0: return {"fired":False,"reason":"empty"}
        inv["ammo"]-=1
        pt=pc["transform"]; level=self._dynamic_level(w)
        best=None
        for e in w["entities"].values():
            if "enemy" not in e.get("tags",[]): continue
            ec=e["components"]; et=ec.get("transform",{})
            dx,dy=et.get("x",0)-pt["x"],et.get("y",0)-pt["y"]
            dist=math.hypot(dx,dy)
            if dist>max_distance or not line_of_sight(level,(pt["x"],pt["y"]),(et.get("x",0),et.get("y",0))): continue
            ang=math.atan2(dy,dx); delta=abs((ang-pt.get("angle",0)+math.pi)%(2*math.pi)-math.pi)
            if delta<0.10 and (best is None or dist<best[0]): best=(dist,e)
        result={"fired":True,"hit":None}
        if best:
            e=best[1]; enemy=e["components"]["enemy"]; enemy["health"]-=damage
            result["hit"]={"entity_id":e["id"],"damage":damage,"health":enemy["health"]}
            if enemy["health"]<=0:
                e["active"]=False; result["hit"]["killed"]=True
                engine.emit(world_id,"enemy.killed",{"entity_id":e["id"]})
        engine.emit(world_id,"weapon.fired",result)
        return result

    def update_pickups(self, engine, world_id):
        w=engine._world(world_id); cfg=w.get("retro_fps")
        if not cfg: return []
        p=w["entities"][cfg["player"]]; pt=p["components"]["transform"]; picked=[]
        for e in w["entities"].values():
            if not e.get("active",True) or "pickup" not in e.get("tags",[]): continue
            t=e["components"].get("transform",{})
            if math.hypot(t.get("x",0)-pt["x"],t.get("y",0)-pt["y"])<0.45:
                pk=e["components"]["pickup"]; kind=pk["kind"]; amt=pk.get("amount",1)
                if kind=="health":
                    pp=p["components"].setdefault("player",{"health":100}); pp["health"]=min(100,pp.get("health",100)+amt)
                elif kind=="ammo":
                    inv=p["components"].setdefault("inventory",{}); inv["ammo"]=inv.get("ammo",0)+amt
                e["active"]=False; picked.append(e["id"]); engine.emit(world_id,"pickup.collected",{"entity_id":e["id"],"kind":kind,"amount":amt})
        return picked

    def update_enemies(self, engine, world_id):
        w=engine._world(world_id); cfg=w.get("retro_fps")
        if not cfg:return
        pid=cfg["player"]; p=w["entities"][pid]; pt=p["components"]["transform"]
        level=self._dynamic_level(w); blocked=[]
        for e in w["entities"].values():
            if not e.get("active",True) or "enemy" not in e.get("tags",[]):continue
            ec=e["components"]; et=ec["transform"]; en=ec["enemy"]
            dist=math.hypot(et["x"]-pt["x"],et["y"]-pt["y"])
            if dist>en.get("aggro_range",8): continue
            if dist<0.8:
                if w["tick"]%10==0:
                    pc=p["components"].setdefault("player",{"health":100,"armor":0})
                    armor=pc.get("armor",0); dmg=en.get("damage",5)
                    absorb=min(armor,dmg//2); pc["armor"]=armor-absorb; pc["health"]=max(0,pc.get("health",100)-(dmg-absorb))
                    engine.emit(world_id,"player.damaged",{"source":e["id"],"damage":dmg-absorb,"health":pc["health"]})
                continue
            path=astar(level,(et["x"],et["y"]),(pt["x"],pt["y"]),blocked)
            if len(path)>1:
                tx,ty=path[1][0]+0.5,path[1][1]+0.5
                dx,dy=tx-et["x"],ty-et["y"]; mag=max(math.hypot(dx,dy),1e-9); sp=en.get("speed",0.05)
                et["x"]+=dx/mag*sp; et["y"]+=dy/mag*sp
