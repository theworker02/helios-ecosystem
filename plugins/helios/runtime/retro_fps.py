from __future__ import annotations
import math

class RetroMap:
    def __init__(self, rows):
        rows = [str(r).rstrip("\n") for r in rows if str(r).strip()]
        if not rows:
            raise ValueError("map cannot be empty")
        width = max(len(r) for r in rows)
        self.rows = [r.ljust(width, "#") for r in rows]
        self.width = width
        self.height = len(self.rows)

    @classmethod
    def from_text(cls, text):
        return cls(text.splitlines())

    def solid(self, x, y):
        ix, iy = int(math.floor(x)), int(math.floor(y))
        if ix < 0 or iy < 0 or ix >= self.width or iy >= self.height:
            return True
        return self.rows[iy][ix] != "."

    def spawn(self):
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                if ch in "P@":
                    return (x + 0.5, y + 0.5)
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                if ch == ".":
                    return (x + 0.5, y + 0.5)
        raise ValueError("map has no walkable cell")

def cast_rays(level, x, y, angle, fov=math.pi/3, rays=64, max_distance=64.0):
    rays = max(1, min(int(rays), 512))
    out = []
    for i in range(rays):
        a = angle - fov/2 + fov * ((i + 0.5) / rays)
        dx, dy = math.cos(a), math.sin(a)
        map_x, map_y = int(x), int(y)
        delta_x = abs(1.0 / dx) if abs(dx) > 1e-9 else 1e30
        delta_y = abs(1.0 / dy) if abs(dy) > 1e-9 else 1e30
        if dx < 0:
            step_x, side_x = -1, (x - map_x) * delta_x
        else:
            step_x, side_x = 1, (map_x + 1.0 - x) * delta_x
        if dy < 0:
            step_y, side_y = -1, (y - map_y) * delta_y
        else:
            step_y, side_y = 1, (map_y + 1.0 - y) * delta_y
        side = 0
        dist = max_distance
        for _ in range(2048):
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
                side = 0
            else:
                side_y += delta_y
                map_y += step_y
                side = 1
            if level.solid(map_x + 0.5, map_y + 0.5):
                dist = (side_x - delta_x) if side == 0 else (side_y - delta_y)
                break
            if min(side_x, side_y) > max_distance:
                break
        corrected = max(0.0001, dist * math.cos(a - angle))
        out.append({"distance": corrected, "raw_distance": dist, "side": side, "cell": [map_x, map_y]})
    return out

def move(level, x, y, angle, forward=0.0, strafe=0.0, turn=0.0, radius=0.18):
    angle += turn
    dx = math.cos(angle) * forward + math.cos(angle + math.pi/2) * strafe
    dy = math.sin(angle) * forward + math.sin(angle + math.pi/2) * strafe
    nx, ny = x + dx, y + dy
    def free(px, py):
        return not any(level.solid(px + ox, py + oy) for ox in (-radius, radius) for oy in (-radius, radius))
    if free(nx, y):
        x = nx
    if free(x, ny):
        y = ny
    return x, y, angle

def ascii_frame(rays, height=24):
    height = max(8, min(int(height), 80))
    width = len(rays)
    canvas = [[" " for _ in range(width)] for _ in range(height)]
    for x, ray in enumerate(rays):
        wall = min(height, max(1, int(height / max(ray["distance"], 0.15))))
        top = max(0, (height - wall)//2)
        bot = min(height, top + wall)
        shade = "█" if ray["distance"] < 2 else "▓" if ray["distance"] < 4 else "▒" if ray["distance"] < 8 else "░"
        for y in range(top, bot):
            canvas[y][x] = shade
        for y in range(bot, height):
            if (x + y) % 3 == 0:
                canvas[y][x] = "."
    return "\n".join("".join(r) for r in canvas)
