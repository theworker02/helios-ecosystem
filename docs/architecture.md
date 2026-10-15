# Helios 1.5 architecture

Helios treats the language model as a controller, designer, director, or agent—not as the authoritative simulation state.

## Runtime layers

1. **World** — deterministic tick/time, scenes, module state, rules, events and input.
2. **ECS-style entities** — entities contain typed components and tags.
3. **Scenes** — named partitions of entities and metadata.
4. **Systems** — built-in deterministic systems such as retro-FPS movement/raycasting plus optional modules.
5. **Events and rules** — bounded event history and declarative condition/effect rules.
6. **Agents** — capability-gated entities that receive bounded observations and submit validated actions.
7. **Persistence** — checkpoints and versioned JSON saves.
8. **MCP** — a tool boundary through which ChatGPT or another compatible agent can create and operate worlds.

The engine intentionally avoids pretending that a chat turn is a real-time 60 FPS loop. A client may request simulation ticks and frames; a local or web renderer can call the same deterministic runtime at higher frequency.


## Forge layer

Forge operates as an independently serializable \`helios.forge/v1\` project stored in the Helios world under \`world["forge"]\`. The existing FPS subsystem remains separate in \`world["retro_fps"]\`, while both share world-level event recording, checkpoints, capability-gated agents and MCP dispatch.

\`ForgeStudio\` is a pure-Python in-memory simulation with declarative maps and actors; it evaluates no user-provided scripts. Project state is JSON-compatible, and each edit/action returns structured results.

\`studio_server.py\` is an **optional loopback-only** HTTP adapter to Helios Core. The \`studio/index.html\` editor uses an HTML Canvas with keyboard controls and calls the local API for authoritative simulation steps; it does not independently simulate game state. The bridge uses a request-size limit and Origin restriction. Do not expose this unauthenticated reference implementation on a public IP address.

Future integrations (a chat app, hosted web renderer, 3D editor, Unity/Godot adapter) should consume the same authoritative Helios actions and project export schema, not fork the rules and create inconsistent simulation results.
