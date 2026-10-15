# Helios Forge v1.5 — multi-genre authoring and play

Helios Forge is a small, deterministic **multi-genre development foundation** integrated into Helios Core. It is not a finished Unity/Unreal replacement or a native high-fidelity renderer. Existing Helios 1.4 FPS tools remain supported.

## Create a project in ChatGPT / via MCP

1. `helios_create_world` with `{"name":"My Game","mode":"forge"}` to obtain a `world_id`.
2. `helios_forge_new` with `{"world_id":"...","name":"My Game","genre":"roguelike","seed":42,"width":24,"height":16}`.
3. `helios_forge_render` to inspect the generated world and HUD.
4. `helios_forge_edit` to paint a tile (`#` wall, `.` floor, `^` hazard).
5. `helios_forge_place` to add actors (`enemy`, `loot`, `goal`, `npc`).
6. `helios_forge_play` to execute actions and read events.
7. `helios_forge_export` / `helios_forge_import` for a portable JSON project.

| Genre | Mechanics | Input |
| --- | --- | --- |
| `roguelike` | Connected seed-generated rooms, turn-based enemy pursuit, combat, loot, win condition | north, south, east, west, attack, wait |
| `topdown` | Top-down movement, combat, loot, dialogue and goals | north, south, east, west, attack, wait |
| `sandbox` | Editable open terrain, buildable walls, event entities | north, south, east, west, attack, wait |
| `platformer` | Gravity, jump, collision, frame-advanced movement, goals and pickups | left, right, jump, left+jump, right+jump, stop, wait |

### Project serialization and bounds

`helios.forge/v1` stores the authored tiles, entity instances, player state, seed, turn and event history as JSON. Defaults are 24×16 and 42 is an example seed. Maximum size is 64×40, with 512 actors, 60 frames per platformer action, and a maximum 500 kB import request. Project deserialization validates the schema; the engine does **not** execute generated scripts.

A game state is held in memory by the running Python process; use explicit export or checkpoint before stopping. A fresh standalone MCP server process does not automatically reopen previous worlds.

### Realistic platform boundaries

- The included stdio MCP server can service capable connected clients, but committing it to GitHub **does not automatically publish or install a ChatGPT plugin**.
- ChatGPT can issue game-creation and play commands when Helios is connected as a tool, but a chat conversation is not a realtime browser rendering loop.
- For responsive graphical play, connect a browser/desktop frontend to the engine. Unity/Godot/Unreal interop would require separate verified adapters and import/export formats.
- This release provides **2D gameplay abstractions**, not real-time 3D, physics-body simulation, network multiplayer or support for importing *any* arbitrary commercial game.

## Run the MCP server

```bash
python core/helios-chatgpt/server/mcp_server.py
```

Use your MCP client to configure the stdio launcher; see `core/helios-chatgpt/.mcp.json` for the existing configuration. Run tests with `python -m pytest -q`.

## What's next

- Renderers: graphical top-down tiles, sprite atlas/animation, canvas/WebGL adapters.
- Authoring: brushes, prefab definitions, regions, incremental world edits, undo/redo.
- AI: bounded NPC planners, agent simulation tests, scripted encounters, automated playtesting.
- Genre plugins: crafting/economy, survival, farming, RTS/building, 3D scene authoring metadata.
- Security: real deployment authentication, per-world isolation, resource and storage limits, validation fuzzing.
