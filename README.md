# Helios Ecosystem 1.3.8

![Helios](./assets/helios-logo.svg)

**Helios is an AI-native game engine built to be driven by ChatGPT, MCP agents, local clients, and conventional front ends.**

Version **1.3.8** moves Helios well beyond a conversational state demo. The repository now contains a deterministic runtime with scenes, ECS-style entities/components, input frames, events, rules, agent capability gates, saves/checkpoints, 20 first-party modules, and a retro-FPS subsystem capable of building and playing **Doom-style** worlds.

Helios does **not** redistribute Doom, proprietary WADs, textures, sounds, maps, or other copyrighted game data. The included WAD reader is for user-supplied files the user is legally entitled to use.

## What Helios can do

- Create and persist multiple game worlds.
- Create scenes and spawn component-based entities.
- Query and patch entity components.
- Install first-party or community modules.
- Advance deterministic simulation ticks.
- Attach AI agents to entities with explicit action capabilities.
- Give agents bounded observations instead of unrestricted world access.
- Apply natural-language-authored structured rules.
- Save, checkpoint, export and import worlds.
- Create grid-based first-person levels and run collision-aware movement.
- Ray-cast retro-FPS frames and render them as structured data or ASCII directly in chat.
- Inspect classic Doom IWAD/PWAD directories and basic map geometry from user-supplied local files.
- Expose the engine through MCP so ChatGPT can operate it through tools rather than merely improvising state.

## Retro FPS quick example

A map is intentionally simple:

```text
############
#..........#
#..###.....#
#.....P....#
#..........#
############
```

ChatGPT can configure that as a world, apply player input, tick the simulation, and request a ray-cast frame. See [examples/retro-fps](./examples/retro-fps).

## Projects

| Project | Purpose |
|---|---|
| **Helios Core** | Deterministic runtime, MCP interface, saves, scenes, ECS-style entities, rules, agents, retro FPS and WAD inspection. |
| **Aether Agents** | Autonomous NPC brains, goals, memories, observations and capability-gated actions. |
| **Echo Dialogue** | Dialogue and conversation state. |
| **Pulse Combat** | Combat resolution and encounter hooks. |
| **Vault Inventory** | Items, equipment and containers. |
| **Forge Crafting** | Recipes and production. |
| **Loom Quests** | Objectives and quest graphs. |
| **Bazaar Economy** | Currency, prices and trading. |
| **Faction Grid** | Reputation, factions and diplomacy. |
| **Vitae Survival** | Health and survival pressures. |
| **Atlas Worlds** | Locations and world generation primitives. |
| **Nimbus Weather** | Weather and environment events. |
| **Drift Vehicles** | Vehicles and traversal. |
| **Hearth Building** | Structures and settlements. |
| **Chronicle State** | Persistence and state history. |
| **Spectra UI** | Renderer-neutral HUD schemas. |
| **Resonance Audio** | Adaptive audio intents. |
| **Relay Multiplayer** | Session and synchronization primitives. |
| **Oracle Director** | AI director/game-master hooks. |
| **Keystone Physics** | Spatial and collision primitives. |
| **Spark SDK** | Third-party module contract and tooling. |

## Run tests

```bash
python -m pytest -q
```

## MCP server

```bash
python core/helios-chatgpt/server/mcp_server.py
```

The MCP tool surface includes world/scene creation, entity operations, module installation, rules, input/ticking, agent attachment/observation/action, retro-FPS setup/rendering, saves and WAD inspection.

## Reality check

Helios can now run a **Doom-like retro FPS simulation**, and it can inspect geometry from classic Doom-format WADs supplied by the user. It is not yet a drop-in replacement for a mature Doom source port: exact BSP rendering, texture composition, specials, full thinker/gameplay compatibility and original asset playback remain additional compatibility work.

## License

MIT.
