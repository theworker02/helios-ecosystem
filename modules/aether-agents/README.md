# Aether Agents

![Aether Agents](./logo.svg)

**Autonomous NPC brains with goals, memories, observations, capability-gated actions, and pluggable agent policies.**

Aether Agents is a first-party **Helios** module. It is intentionally isolated behind the Helios module contract so games can enable, replace, or extend this subsystem without modifying Helios Core.

## Install into a world

```python
from module import install
install(world)
```

## Contract

- Module id: `aether-agents`
- Category: `agent`
- Runtime: Python reference implementation
- State ownership: `world.modules.aether-agents`
- Integration: event-driven, capability-safe

## Status

Experimental 0.x reference module. The public contract is designed to deepen without forcing changes into Helios Core.
