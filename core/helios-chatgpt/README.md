# Helios Core

Helios Core is the deterministic world runtime behind the Helios ecosystem. It models worlds, entities, systems, events, rules, turns, agents, checkpoints and portable state. ChatGPT or another MCP-capable client can act as the conversational controller without becoming the source of truth for game state.

## Goals

- deterministic state transitions
- bounded agent observations and capability-gated actions
- modular mechanics
- portable JSON state
- chat-first turn execution
- safe local-first extension points
