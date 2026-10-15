# Helios Ecosystem 1.5.0

![Helios](./assets/helios-logo.svg)

**Helios is an AI-native game engine built for ChatGPT, MCP agents, local clients, and conventional renderers.**

v1.4.0 deepened Helios from a retro-FPS foundation into a playable game runtime: enemies, A* navigation, health/armor, ammo, hitscan combat, pickups, interactive doors, deterministic replay logs, HUD state, resource-pack manifests, scenes, ECS-style entities, agent capability gates, rules, checkpoints, and 20 first-party modules.

## Helios Forge Studio (new in 1.5)

Helios Forge adds a **multi-genre game-authoring and playing layer**, powered by the same deterministic Helios Core runtime. Available prototypes: \`roguelike\`, \`topdown\`, \`sandbox\` and \`platformer\`. Create seeded maps, paint tiles, place enemies/loot/dialogue NPCs/goals, fight, jump, collect, export/import and use MCP to control worlds.

A local **HTML5 Canvas game editor** uses an HTTP bridge to Helios Python rather than implementing a divergent JavaScript simulation:

\`\`\`bash
python core/helios-chatgpt/server/studio_server.py
# Visit http://127.0.0.1:8787
\`\`\`

This reference server is **loopback-only**: it is not ready for public deployment. ChatGPT MCP connection still requires installing/hosting an accessible tool integration; adding source code here alone does not make it available to every ChatGPT account.

See [Forge guide](docs/forge.md) for the exact seven MCP tools, supported mechanics and limitations.

## Playable retro-FPS loop

A map can now contain:

```text
################
#P....A........#
#..####...E....#
#..............#
#...D..........#
#........+.....#
#......E.......#
################
```

Symbols: `P` player, `E` enemy, `A` ammo, `+` health, `D` door, `#` wall.

ChatGPT can create the world, move/turn the player, tick enemies, fire a weapon, open doors, collect pickups, read the HUD, render a ray-cast frame, checkpoint, save and export a replay.

## Major engine layers

- deterministic world/tick runtime
- ECS-style entities/components/tags
- scenes and active-scene switching
- structured events and declarative rules
- deterministic RNG
- capability-gated AI agents
- A* pathfinding and line-of-sight
- retro-FPS movement/collision/raycasting
- enemies, combat, pickups and doors
- HUD/gameplay state
- resource-pack manifests
- replay/input logs
- checkpoints and versioned saves
- MCP tool surface for ChatGPT
- classic Doom IWAD/PWAD metadata/geometry inspection for user-supplied files
- 20 first-party gameplay/developer modules

## Doom-style support

Helios can run original Doom-like gameplay and inspect classic Doom WAD structure supplied by the user. It does not bundle or redistribute Doom, original WADs, maps, textures, sounds or other proprietary assets.

It is still not claiming exact source-port compatibility. Exact Doom BSP rendering, texture compositing, sector specials, thinkers, sprite animation and compatibility quirks remain future work.

## Run

```bash
python -m pytest -q
python core/helios-chatgpt/server/mcp_server.py
```

See `docs/gameplay.md`, `docs/architecture.md`, and `examples/retro-fps/`.

## License

MIT.
