# Helios 1.3.8 architecture

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
