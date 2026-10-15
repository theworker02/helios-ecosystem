# Pulse Combat

![Pulse Combat](./logo.svg)

**Turn-based combat resolution with stats, damage types, status effects, targeting, and encounter hooks.**

Pulse Combat is a first-party **Helios** module. It is intentionally isolated behind the Helios module contract so games can enable, replace, or extend this subsystem without modifying Helios Core.

## Install into a world

```python
from module import install
install(world)
```

## Contract

- Module id: `pulse-combat`
- Category: `combat`
- Runtime: Python reference implementation
- State ownership: `world.modules.pulse-combat`
- Integration: event-driven, capability-safe

## Status

Experimental 0.x reference module. The public contract is designed to deepen without forcing changes into Helios Core.
