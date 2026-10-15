# Gameplay runtime

Helios 1.4.0 adds first-class gameplay state to the retro-FPS subsystem.

Map symbols:
- `#` wall
- `.` floor
- `P` player spawn
- `E` enemy spawn
- `+` health pickup
- `A` ammo pickup
- `D` interactive door

The engine converts enemy and pickup symbols into ECS entities and keeps doors as dynamic collision cells. The runtime includes health, armor, ammo, hitscan firing, pickups, simple enemy navigation, contact attacks, and a HUD snapshot.

Enemy movement uses deterministic A* over the current collision map. The design intentionally favors inspectable deterministic behavior over hidden model-driven movement.
