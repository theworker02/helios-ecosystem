# Echo Dialogue

![Echo Dialogue](./logo.svg)

**Branching and agent-driven dialogue, relationship context, conversation memory, and dialogue events.**

Echo Dialogue is a first-party **Helios** module. It is intentionally isolated behind the Helios module contract so games can enable, replace, or extend this subsystem without modifying Helios Core.

## Install into a world

```python
from module import install
install(world)
```

## Contract

- Module id: `echo-dialogue`
- Category: `dialogue`
- Runtime: Python reference implementation
- State ownership: `world.modules.echo-dialogue`
- Integration: event-driven, capability-safe

## Status

Experimental 0.x reference module. The public contract is designed to deepen without forcing changes into Helios Core.
