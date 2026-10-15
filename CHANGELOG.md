# Changelog

## 1.3.8

Helios 1.3.8 promotes the project from an experimental state container into an AI-native game runtime.

### Engine
- ECS-style entity/component storage with indexed queries.
- Multi-scene world state and active-scene switching.
- Deterministic tick loop, input frames, events, rules, and checkpoints.
- Module lifecycle registry and per-world module state.
- Capability-gated agent attachments, observations, and actions.
- Portable JSON save/import format with engine versioning.

### Retro FPS
- Tile/grid world loader.
- DDA ray-caster with configurable field of view and ray count.
- Collision-aware first-person movement.
- ASCII frame renderer for text-native clients.
- Classic Doom WAD directory reader and geometry metadata parser for user-supplied, legally owned WAD files.
- Example retro-FPS arena.

### ChatGPT / MCP
- Tools for creating worlds/scenes, spawning entities, installing modules, attaching agents, applying input, ticking simulations, ray-casting views, querying state, checkpointing, exporting, importing, and inspecting WAD metadata.

Helios does not bundle or redistribute Doom, Doom assets, or proprietary WAD data.
