from __future__ import annotations
import copy

OPS = {
    "eq": lambda a,b: a == b,
    "ne": lambda a,b: a != b,
    "lt": lambda a,b: a < b,
    "lte": lambda a,b: a <= b,
    "gt": lambda a,b: a > b,
    "gte": lambda a,b: a >= b,
    "contains": lambda a,b: b in a,
}

def get_path(obj, path, default=None):
    cur = obj
    for part in str(path).split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def set_path(obj, path, value):
    parts = str(path).split(".")
    cur = obj
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = copy.deepcopy(value)

def evaluate(rule, context):
    cond = rule.get("when") or {}
    op = OPS.get(cond.get("op","eq"))
    if not op:
        return False
    return op(get_path(context, cond.get("path","")), cond.get("value"))

def apply_effect(effect, context):
    kind = effect.get("type","set")
    path = effect.get("path")
    if kind == "set":
        set_path(context, path, effect.get("value"))
    elif kind == "increment":
        set_path(context, path, (get_path(context,path,0) or 0) + effect.get("value",1))
    else:
        raise ValueError("unsupported effect type")
