from __future__ import annotations
import random

class DeterministicRng:
    def __init__(self, seed=0):
        self.seed = int(seed)
        self._r = random.Random(self.seed)
        self.draws = 0

    def random(self):
        self.draws += 1
        return self._r.random()

    def randint(self, a, b):
        self.draws += 1
        return self._r.randint(a, b)

    def choice(self, seq):
        if not seq:
            raise ValueError("cannot choose from empty sequence")
        self.draws += 1
        return self._r.choice(seq)

    def state(self):
        return {"seed": self.seed, "draws": self.draws}
