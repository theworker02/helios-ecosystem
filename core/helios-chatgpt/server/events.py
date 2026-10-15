from __future__ import annotations
import copy

class EventBus:
    def __init__(self, history=None, max_history=2048):
        self.history = list(history or [])
        self.max_history = max_history
        self._queue = []

    def emit(self, event_type, payload=None, tick=0, source="engine"):
        event = {
            "type": str(event_type),
            "payload": copy.deepcopy(payload or {}),
            "tick": int(tick),
            "source": source,
        }
        self._queue.append(event)
        self.history.append(copy.deepcopy(event))
        if len(self.history) > self.max_history:
            del self.history[:-self.max_history]
        return copy.deepcopy(event)

    def drain(self):
        q = self._queue
        self._queue = []
        return copy.deepcopy(q)
