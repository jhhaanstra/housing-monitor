#!/usr/bin/env python

from time import sleep
from uuid import UUID

from model.model import Advertisement
from targets.target import Target


class Monitor:
    interval: int
    targets: list[Target]
    running: bool

    stored: {Target: list[UUID]}

    def __init__(self, interval, targets) -> None:
        super().__init__()
        self.interval = interval
        self.targets = targets
        self.stored = {target: [] for target in targets}

    def start(self) -> None:
        self.running = True

        while self.running:
            sleep(self.interval)

    def run(self) -> [Advertisement]:
        results: [Advertisement] = list()

        for target in self.targets:
            for ad in target.get_advertisements():
                if ad.id not in self.stored[target]:
                    self.stored[target].append(ad.id)
                    results.append(ad)

        return results
