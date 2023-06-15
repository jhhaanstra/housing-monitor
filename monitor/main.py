#!/usr/bin/env python

from time import sleep

from targets.target import Target


class Monitor:
    interval: int
    targets: list[Target]
    running: bool

    def __init__(self, interval, min_price, max_price, min_surface) -> None:
        self.interval = interval
        self.min_price = min_price
        self.max_price = max_price
        self.min_surface = min_surface
        super().__init__()

    def start(self) -> None:
        self.running = True

        while self.running:
            sleep(self.interval)


