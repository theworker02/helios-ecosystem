# Doom-style games in Helios

Helios 1.3.8 adds the first production-oriented retro-FPS path.

## What works
- grid-based first-person maps;
- player pose and collision-aware movement;
- DDA wall ray casting;
- configurable FOV and ray count;
- ASCII/text frame rendering for chat surfaces;
- entities, combat/inventory/AI modules around the FPS world;
- user-supplied classic Doom WAD directory and geometry metadata inspection.

## What "run Doom" means here

Helios can now support games in the **classic Doom-like design space** and can read geometry metadata from legally obtained classic WADs. It does not contain the original Doom engine, game data, textures, sounds, levels, or copyrighted assets.

A full source-port-compatible Doom runtime would additionally need BSP traversal, exact linedef/sidedef behavior, texture compositing, flats, sprites, specials, thinkers, weapon/game logic, audio playback and compatibility handling. Those are future compatibility layers rather than claims made by v1.3.8.
