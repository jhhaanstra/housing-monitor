from time import sleep
from uuid import UUID

from model.model import Advertisement
from targets.pandomo import Pandomo
from targets.target import Target, TargetConfig


class TargetBuilder:

    @staticmethod
    def build_target(target: str, target_config: TargetConfig) -> Target:
        match target.lower():
            case 'pandomo':
                return Pandomo(target_config)
            case _:
                raise ValueError(target + " is not a valid target, please update the config")


class Monitor:
    interval: int
    targets: list[Target]
    stored: {Target: list[UUID]}

    def __init__(self, interval, targets, target_config) -> None:
        super().__init__()
        self.interval = interval
        self.targets = [TargetBuilder.build_target(target, target_config) for target in targets]
        self.stored = {target: [] for target in targets}

    def start(self) -> None:
        running = True

        while running:
            sleep(self.interval)

    def run(self) -> [Advertisement]:
        results: [Advertisement] = list()

        for target in self.targets:
            for ad in target.get_advertisements():
                if ad.id not in self.stored[target]:
                    self.stored[target].append(ad.id)
                    results.append(ad)

        return results
