---
name: game-builder
description: Build and play deterministic games via Helios MCP tools from ChatGPT Desktop.
---

# Helios Game Builder

Use Helios MCP tools as the **authoritative** game state. Never narrate unexecuted actions as if they occurred.

## 2D Forge

Call `helios_create_world`, save its world_id, then `helios_forge_new` with genre `roguelike`, `topdown`, `platformer`, or `sandbox`. Call `helios_forge_render` to display the actual map and HUD. Use `helios_forge_edit` to edit tiles, `helios_forge_place` to place actors, `helios_forge_play` to simulate actions, `helios_forge_export` and `helios_forge_import` for portable saves. Grid actions: north/south/east/west/attack/wait. Platform actions: left/right/jump/left+jump/right+jump/stop/wait.

## Retro FPS

Call `helios_create_world`, then `helios_configure_retro_fps` with a map containing P (player), E (enemy), A (ammo), D (door), + (health), # (wall). `helios_apply_input` and `helios_tick` move; `helios_fire_weapon`, `helios_interact`, `helios_raycast_frame`, and `helios_get_hud` play and inspect. Use `helios_export_world`, `helios_checkpoint`, and `helios_export_replay` when appropriate.

## Limitations

The MCP client controls a deterministic Python simulation; ChatGPT does not render games at 60 FPS or offer complete 3D gameplay inside a chat. State is lost if the local process ends without export. Do not inspect local files or overwrite projects without an explicit user request.
