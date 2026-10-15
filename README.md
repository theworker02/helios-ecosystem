# Helios Ecosystem

![Helios](./assets/helios-logo.svg)

**Helios is an AI-native mini game engine designed to be controlled conversationally and extended by agents.** This monorepo contains the Helios ChatGPT/MCP engine plus 20 first-party gameplay and developer modules.

Instead of making an LLM improvise an entire game as prose, Helios gives the conversation an explicit world model: entities, components, systems, events, rules, agents, turns, checkpoints, and portable state. Agents act through declared capabilities rather than receiving unrestricted control.

## Projects

| Project | Purpose |
|---|---|
| **Helios Core** | Stateful AI-native mini game engine and ChatGPT/MCP integration. |
| [Aether Agents](./modules/aether-agents) | Autonomous NPC brains with goals, memories, observations, capability-gated actions, and pluggable agent policies. |
| [Echo Dialogue](./modules/echo-dialogue) | Branching and agent-driven dialogue, relationship context, conversation memory, and dialogue events. |
| [Pulse Combat](./modules/pulse-combat) | Turn-based combat resolution with stats, damage types, status effects, targeting, and encounter hooks. |
| [Vault Inventory](./modules/vault-inventory) | Items, containers, equipment slots, stack rules, ownership, transfers, loot, and inventories. |
| [Forge Crafting](./modules/forge-crafting) | Recipes, ingredients, tools, stations, crafting queues, quality, and production events. |
| [Loom Quests](./modules/loom-quests) | Objectives, quest graphs, prerequisites, branching outcomes, rewards, and progression tracking. |
| [Bazaar Economy](./modules/bazaar-economy) | Currencies, shops, pricing, scarcity, trade, inventories, and configurable market simulation. |
| [Faction Grid](./modules/faction-grid) | Factions, membership, reputation, diplomacy, hostility, alliances, territory claims, and social state. |
| [Vitae Survival](./modules/vitae-survival) | Health, hunger, thirst, fatigue, temperature, disease, injury, recovery, and survival pressure. |
| [Atlas Worlds](./modules/atlas-worlds) | World, region, scene, biome, location, travel, and procedural world-generation primitives. |
| [Nimbus Weather](./modules/nimbus-weather) | Weather states, climate transitions, time-of-day modifiers, hazards, and environment events. |
| [Drift Vehicles](./modules/drift-vehicles) | Vehicles, fuel, cargo, seats, durability, traversal costs, routes, and vehicle actions. |
| [Hearth Building](./modules/hearth-building) | Construction, structures, rooms, placement, upgrades, utilities, ownership, and settlement state. |
| [Chronicle State](./modules/chronicle-state) | Save games, checkpoints, snapshots, rollback-safe histories, migrations, and portable world persistence. |
| [Spectra UI](./modules/spectra-ui) | Declarative HUDs, panels, menus, meters, interaction prompts, and renderer-neutral presentation schemas. |
| [Resonance Audio](./modules/resonance-audio) | Music states, ambient layers, sound cues, spatial audio intents, and adaptive soundtrack events. |
| [Relay Multiplayer](./modules/relay-multiplayer) | Player sessions, authority rules, state deltas, turn synchronization, presence, and co-op primitives. |
| [Oracle Director](./modules/oracle-director) | AI game-master and narrative-director hooks for pacing, encounters, tension, goals, and adaptive story beats. |
| [Keystone Physics](./modules/keystone-physics) | Lightweight spatial rules, collision intents, movement costs, occupancy, ranges, and deterministic resolution. |
| [Spark SDK](./modules/spark-sdk) | Developer-facing module SDK, manifests, hooks, schemas, compatibility checks, examples, and module test harnesses. |

## Repository layout

```text
core/helios-chatgpt/   ChatGPT/MCP Helios runtime
modules/               20 first-party modules
sdk/                   shared module API
assets/                Helios brand assets
registry.json          machine-readable module registry
tests/                 ecosystem smoke tests
```

## Quick start

```bash
python core/helios-chatgpt/server/mcp_server.py
```

For local module development, each folder under `modules/` contains a `module.json`, reference `module.py`, documentation, and a dedicated SVG logo.

Run the ecosystem tests with:

```bash
python -m pytest tests core/helios-chatgpt/tests
```

## Design principles

- **AI-native, not AI-dependent:** deterministic engine state remains authoritative.
- **Capability-gated agents:** NPCs and external agents receive bounded observations/actions.
- **Composable modules:** mechanics are isolated behind manifests and events.
- **Portable worlds:** save/import without tying a game to one model vendor.
- **Chat-first:** the engine can be driven naturally from ChatGPT or another MCP-capable client.
- **Open ecosystem:** module manifests and runtime interfaces are designed for community extensions.

## Status

Helios is experimental (`0.x`). The engine is functional, while the 20 first-party modules currently provide the module contract, manifests, event integration, isolated state, and extensible reference implementations. Their deeper mechanics are intended to evolve independently without destabilizing the core runtime.

## License

MIT.
