# Replays

Helios records high-value input/action events into a replay log. Replay data uses the `helios.replay/v1` schema and is portable JSON.

The replay stream is designed to support deterministic reproduction of player inputs, agent actions and simulation ticks. Asset packs are referenced separately rather than embedded into replay files.
