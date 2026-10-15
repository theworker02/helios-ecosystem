"""Helios Forge: deterministic, serializable, multi-genre 2D gameplay studio.

The forge state contains only JSON values. No generated code or arbitrary scripts
are executed by the runtime, making it suitable for capability-gated MCP tools.
"""
from __future__ import annotations

import copy
import json
import math
import random

SCHEMA = "helios.forge/v1"
GENRES = {"roguelike", "topdown", "platformer", "sandbox"}
TILES = {"#", ".", "^"}
KINDS = {"enemy", "loot", "goal", "npc"}


def _passable(project, x, y):
    x, y = int(math.floor(x)), int(math.floor(y))
    return (0 <= x < project["width"] and 0 <= y < project["height"]
            and project["tiles"][y][x] != "#")


def _solid(project, x, y, radius=0.25):
    return any(not _passable(project, x + dx, y + dy)
               for dx in (-radius, radius) for dy in (-radius, radius))


def _actor_at(project, x, y, kind=None):
    for actor in project["actors"]:
        if actor.get("active", True) and int(actor["x"]) == int(x) and int(actor["y"]) == int(y):
            if kind is None or actor["kind"] == kind:
                return actor
    return None


class ForgeStudio:
    """Author and play one genre-neutral project in an existing Helios world."""

    @staticmethod
    def create(name, genre="roguelike", seed=0, width=24, height=16):
        if genre not in GENRES:
            raise ValueError("unsupported Forge genre")
        width, height, seed = int(width), int(height), int(seed)
        if not (8 <= width <= 64 and 8 <= height <= 40):
            raise ValueError("Forge dimensions must be 8..64 by 8..40")
        rng = random.Random(seed)
        rows = [["#" for _ in range(width)] for _ in range(height)]
        actors = []
        if genre == "platformer":
            for y in range(height - 1):
                for x in range(1, width - 1):
                    rows[y][x] = "."
            for x in range(1, width - 1):
                rows[height - 1][x] = "#"
            for x in range(4, width - 3, 6):
                y = height - 4 - ((x // 6) % 2)
                for bx in range(x, min(x + 3, width - 1)):
                    rows[y][bx] = "#"
            start = (2, height - 2)
            actors = [
                {"id": "coin_1", "kind": "loot", "x": min(width - 3, 6),
                 "y": height - 2, "value": 10, "active": True},
                {"id": "finish", "kind": "goal", "x": width - 2,
                 "y": height - 2, "active": True},
            ]
        elif genre == "sandbox":
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    rows[y][x] = "."
            start = (width // 2, height // 2)
        else:
            # Carve seeded rooms and corridors. Every carved room remains connected.
            centers = []
            attempts = max(6, min(18, width * height // 45))
            for _ in range(attempts):
                rw = rng.randint(3, min(8, width - 2))
                rh = rng.randint(3, min(6, height - 2))
                x = rng.randint(1, width - rw - 1)
                y = rng.randint(1, height - rh - 1)
                for yy in range(y, y + rh):
                    for xx in range(x, x + rw):
                        rows[yy][xx] = "."
                center = (x + rw // 2, y + rh // 2)
                if centers:
                    px, py = centers[-1]
                    if rng.randrange(2):
                        for xx in range(min(px, center[0]), max(px, center[0]) + 1):
                            rows[py][xx] = "."
                        for yy in range(min(py, center[1]), max(py, center[1]) + 1):
                            rows[yy][center[0]] = "."
                    else:
                        for yy in range(min(py, center[1]), max(py, center[1]) + 1):
                            rows[yy][px] = "."
                        for xx in range(min(px, center[0]), max(px, center[0]) + 1):
                            rows[center[1]][xx] = "."
                centers.append(center)
            start = centers[0]
            reachable = [(x, y) for y in range(1, height - 1)
                         for x in range(1, width - 1) if rows[y][x] == "." and (x, y) != start]
            reachable.sort(key=lambda p: abs(p[0] - start[0]) + abs(p[1] - start[1]), reverse=True)
            occupied = {start}
            for kind, value in (("goal", 0), ("enemy", 0), ("enemy", 0),
                                ("loot", 15), ("loot", 15)):
                candidates = [p for p in reachable if p not in occupied]
                if not candidates:
                    break
                pos = candidates[0] if kind == "goal" else rng.choice(candidates)
                occupied.add(pos)
                actor = {"id": f"{kind}_{len(actors)}", "kind": kind,
                         "x": pos[0], "y": pos[1], "active": True}
                if kind == "enemy":
                    actor["hp"] = 35
                if kind == "loot":
                    actor["value"] = value
                actors.append(actor)
        player = {"x": start[0], "y": start[1], "vx": 0.0, "vy": 0.0,
                  "grounded": genre == "platformer", "health": 100, "score": 0,
                  "inventory": []}
        return {"schema": SCHEMA, "name": str(name)[:120], "genre": genre,
                "seed": seed, "width": width, "height": height,
                "tiles": ["".join(row) for row in rows],
                "player": player, "actors": actors, "turn": 0,
                "completed": False, "events": []}

    @staticmethod
    def validate(project):
        if not isinstance(project, dict) or project.get("schema") != SCHEMA:
            raise ValueError("unsupported Forge project schema")
        w, h = project.get("width"), project.get("height")
        if type(w) is not int or type(h) is not int or not (8 <= w <= 64 and 8 <= h <= 40):
            raise ValueError("invalid Forge dimensions")
        if project.get("genre") not in GENRES:
            raise ValueError("invalid Forge genre")
        tiles = project.get("tiles")
        if (not isinstance(tiles, list) or len(tiles) != h or
            any(not isinstance(row, str) or len(row) != w or not set(row) <= TILES
                for row in tiles)):
            raise ValueError("invalid Forge tile data")
        p = project.get("player")
        if not isinstance(p, dict) or any(not isinstance(p.get(k), (int, float)) or
                                        not math.isfinite(p[k]) for k in ("x", "y", "health", "score")):
            raise ValueError("invalid Forge player")
        if not _passable(project, p["x"], p["y"]):
            raise ValueError("player must stand on a passable tile")
        actors = project.get("actors")
        if not isinstance(actors, list) or len(actors) > 512:
            raise ValueError("invalid Forge actor list")
        ids = set()
        for actor in actors:
            if (not isinstance(actor, dict) or not isinstance(actor.get("id"), str)
                or not actor["id"] or actor["id"] in ids or actor.get("kind") not in KINDS
                or type(actor.get("x")) is not int or type(actor.get("y")) is not int
                or not _passable(project, actor["x"], actor["y"])):
                raise ValueError("invalid or duplicate Forge actor")
            ids.add(actor["id"])
        # Imported projects are untrusted: validate all fields consumed by play
        # and render rather than accepting an incomplete v1-shaped dictionary.
        if (not isinstance(project.get("name"), str) or len(project["name"]) > 120
            or type(project.get("seed")) is not int or
            type(project.get("turn")) is not int or project["turn"] < 0 or
            type(project.get("completed")) is not bool):
            raise ValueError("invalid Forge project metadata")
        if (type(p.get("grounded")) is not bool
            or not isinstance(p.get("inventory"), list)
            or len(p["inventory"]) > 512
            or any(not isinstance(item, str) or len(item) > 80 for item in p["inventory"])):
            raise ValueError("invalid Forge player inventory or physics state")
        for k in ("vx", "vy"):
            if not isinstance(p.get(k), (int, float)) or not math.isfinite(p[k]) or abs(p[k]) > 100:
                raise ValueError("invalid Forge player velocity")
        if not 0 <= p["health"] <= 10000 or not 0 <= p["score"] <= 1_000_000_000:
            raise ValueError("invalid Forge health or score")
        for actor in actors:
            if type(actor.get("active")) is not bool:
                raise ValueError("invalid Forge actor state")
            if actor["kind"] == "enemy" and (
                type(actor.get("hp")) is not int or not -10000 <= actor["hp"] <= 10000):
                raise ValueError("invalid Forge enemy health")
            if actor["kind"] == "loot" and (
                type(actor.get("value")) is not int or not 1 <= actor["value"] <= 10000):
                raise ValueError("invalid Forge loot amount")
            if actor["kind"] == "npc" and (
                not isinstance(actor.get("dialogue"), str) or len(actor["dialogue"]) > 500):
                raise ValueError("invalid Forge dialogue")
        events = project.get("events")
        if (not isinstance(events, list) or len(events) > 100
            or any(not isinstance(e, dict) or not isinstance(e.get("type"), str)
                   or len(e["type"]) > 120 for e in events)):
            raise ValueError("invalid Forge event history")
        return copy.deepcopy(project)

    @staticmethod
    def edit(project, x, y, tile):
        x, y = int(x), int(y)
        if tile not in TILES:
            raise ValueError("unknown tile; use #, . or ^")
        if not (0 <= x < project["width"] and 0 <= y < project["height"]):
            raise ValueError("tile outside project")
        if tile == "#" and ((int(project["player"]["x"]), int(project["player"]["y"])) == (x, y)
                            or _actor_at(project, x, y)):
            raise ValueError("cannot build a wall over player or actor")
        row = list(project["tiles"][y])
        row[x] = tile
        project["tiles"][y] = "".join(row)
        return {"x": x, "y": y, "tile": tile}

    @staticmethod
    def place(project, actor_id, kind, x, y, hp=35, value=10, dialogue=""):
        if kind not in KINDS:
            raise ValueError("unknown actor kind")
        if not isinstance(actor_id, str) or not actor_id or len(actor_id) > 80:
            raise ValueError("invalid actor id")
        x, y = int(x), int(y)
        if not _passable(project, x, y):
            raise ValueError("actors require walkable tiles")
        if any(a["id"] == actor_id for a in project["actors"]) or len(project["actors"]) >= 512:
            raise ValueError("duplicate actor id or actor limit reached")
        if _actor_at(project, x, y) or (int(project["player"]["x"]), int(project["player"]["y"])) == (x, y):
            raise ValueError("tile is occupied")
        a = {"id": actor_id, "kind": kind, "x": x, "y": y, "active": True}
        if kind == "enemy":
            a["hp"] = max(1, min(10000, int(hp)))
        elif kind == "loot":
            a["value"] = max(1, min(10000, int(value)))
        elif kind == "npc":
            a["dialogue"] = str(dialogue)[:500]
        project["actors"].append(a)
        return copy.deepcopy(a)

    @staticmethod
    def _collect(project, events):
        p = project["player"]
        for actor in project["actors"]:
            if not actor["active"] or int(actor["x"]) != int(p["x"]) or int(actor["y"]) != int(p["y"]):
                continue
            if actor["kind"] == "loot":
                actor["active"] = False
                p["score"] += int(actor.get("value", 10))
                p["inventory"].append(actor["id"])
                events.append({"type": "loot.collected", "id": actor["id"]})
            elif actor["kind"] == "goal":
                project["completed"] = True
                events.append({"type": "goal.reached", "id": actor["id"]})
            elif actor["kind"] == "npc":
                events.append({"type": "npc.speaks", "id": actor["id"],
                               "text": actor.get("dialogue", "")})

    @staticmethod
    def _grid_turn(project, action, events):
        dirs = {"north": (0, -1), "south": (0, 1),
                "west": (-1, 0), "east": (1, 0)}
        if action not in (*dirs, "wait", "attack"):
            raise ValueError("invalid grid action")
        p = project["player"]
        if action in dirs:
            dx, dy = dirs[action]
            nx, ny = int(p["x"]) + dx, int(p["y"]) + dy
            enemy = _actor_at(project, nx, ny, "enemy")
            if enemy:
                enemy["hp"] -= 20
                events.append({"type": "combat.player_hit", "id": enemy["id"], "hp": enemy["hp"]})
                if enemy["hp"] <= 0:
                    enemy["active"] = False
                    p["score"] += 25
                    events.append({"type": "enemy.defeated", "id": enemy["id"]})
            elif _passable(project, nx, ny):
                p["x"], p["y"] = nx, ny
            else:
                events.append({"type": "movement.blocked"})
        elif action == "attack":
            target = next((a for a in project["actors"] if a["active"] and a["kind"] == "enemy"
                           and abs(a["x"] - p["x"]) + abs(a["y"] - p["y"]) == 1), None)
            if target:
                target["hp"] -= 20
                events.append({"type": "combat.player_hit", "id": target["id"], "hp": target["hp"]})
                if target["hp"] <= 0:
                    target["active"] = False
                    p["score"] += 25
                    events.append({"type": "enemy.defeated", "id": target["id"]})
        ForgeStudio._collect(project, events)
        if project["genre"] == "roguelike" and not project["completed"]:
            for actor in project["actors"]:
                if not actor["active"] or actor["kind"] != "enemy":
                    continue
                distance = abs(actor["x"] - p["x"]) + abs(actor["y"] - p["y"])
                if distance == 1:
                    p["health"] = max(0, p["health"] - 5)
                    events.append({"type": "combat.player_damaged", "id": actor["id"], "amount": 5})
                elif 1 < distance <= 7:
                    dx = (1 if p["x"] > actor["x"] else -1 if p["x"] < actor["x"] else 0)
                    dy = (1 if p["y"] > actor["y"] else -1 if p["y"] < actor["y"] else 0)
                    for nx, ny in ((actor["x"] + dx, actor["y"]), (actor["x"], actor["y"] + dy)):
                        if (_passable(project, nx, ny) and
                            (int(p["x"]), int(p["y"])) != (nx, ny) and
                            not _actor_at(project, nx, ny)):
                            actor["x"], actor["y"] = nx, ny
                            break

    @staticmethod
    def _platform_frames(project, action, frames, events):
        if action not in {"left", "right", "jump", "left+jump", "right+jump", "stop", "wait"}:
            raise ValueError("invalid platformer action")
        p = project["player"]
        horizontal = (-1 if "left" in action else 1 if "right" in action else 0)
        if "jump" in action and p.get("grounded", False):
            p["vy"] = -0.55
            p["grounded"] = False
            events.append({"type": "player.jumped"})
        for _ in range(frames):
            p["vx"] = horizontal * 0.19
            if not _solid(project, p["x"] + p["vx"], p["y"]):
                p["x"] += p["vx"]
            p["vy"] = min(0.45, p.get("vy", 0) + 0.075)
            dy = p["vy"]
            p["grounded"] = False
            # Small swept steps avoid passing through thin floors at terminal speed.
            n = max(1, int(math.ceil(abs(dy) / 0.10)))
            for _ in range(n):
                step = dy / n
                if _solid(project, p["x"], p["y"] + step):
                    if dy > 0:
                        p["grounded"] = True
                    p["vy"] = 0.0
                    break
                p["y"] += step
            ForgeStudio._collect(project, events)
            if project["tiles"][int(p["y"])][int(p["x"])] == "^":
                p["health"] = max(0, p["health"] - 2)
                events.append({"type": "hazard.damage", "amount": 2})
            if project["completed"] or p["health"] <= 0:
                break

    @staticmethod
    def play(project, action, frames=1):
        if project["completed"]:
            return {"turn": project["turn"], "completed": True, "events": []}
        if project["player"]["health"] <= 0:
            return {"turn": project["turn"], "game_over": True, "events": []}
        frames = int(frames)
        if not 1 <= frames <= 60:
            raise ValueError("frames must be 1..60")
        events = []
        if project["genre"] == "platformer":
            ForgeStudio._platform_frames(project, action, frames, events)
        else:
            if frames != 1:
                raise ValueError("grid games advance exactly one turn per action")
            ForgeStudio._grid_turn(project, action, events)
            p = project["player"]
            if project["tiles"][int(p["y"])][int(p["x"])] == "^":
                p["health"] = max(0, p["health"] - 5)
                events.append({"type": "hazard.damage", "amount": 5})
        project["turn"] += frames if project["genre"] == "platformer" else 1
        project["events"] = (project.get("events", []) + events)[-100:]
        return {"turn": project["turn"], "completed": project["completed"],
                "game_over": project["player"]["health"] <= 0,
                "player": copy.deepcopy(project["player"]), "events": events}

    @staticmethod
    def render(project):
        chars = [list(row) for row in project["tiles"]]
        for actor in project["actors"]:
            if not actor.get("active", True):
                continue
            glyph = {"enemy": "E", "loot": "$", "goal": "X", "npc": "N"}[actor["kind"]]
            chars[actor["y"]][actor["x"]] = glyph
        p = project["player"]
        chars[int(p["y"])][int(p["x"])] = "@"
        return {"ascii": "\n".join("".join(row) for row in chars),
                "hud": {"genre": project["genre"], "turn": project["turn"],
                        "health": p["health"], "score": p["score"],
                        "inventory": copy.deepcopy(p["inventory"]),
                        "completed": project["completed"]},
                "legend": {"@": "player", "#": "solid", ".": "floor",
                           "^": "hazard", "E": "enemy", "$": "loot",
                           "X": "goal", "N": "NPC"}}

    @staticmethod
    def export(project):
        ForgeStudio.validate(project)
        return json.dumps(project, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def import_project(payload):
        if not isinstance(payload, str) or len(payload) > 500000:
            raise ValueError("invalid or oversized project JSON")
        try:
            project = json.loads(payload)
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid project JSON") from exc
        return ForgeStudio.validate(project)
