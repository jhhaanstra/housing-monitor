from time import sleep

import notifypy

from model.model import Advertisement
from targets.dcwonen import DcWonen
from targets.grunoverhuur import GrunoVerhuur
from targets.kpmakelaars import KpMakelaars
from targets.pandomo import Pandomo
from targets.pararius import Pararius
from targets.target import Target, TargetConfig


class TargetBuilder:

    @staticmethod
    def build_target(target: str, target_config: TargetConfig) -> Target:
        match target.lower():
            case 'pandomo':
                return Pandomo(target_config)
            case 'dcwonen':
                return DcWonen(target_config)
            case 'kpmakelaars':
                return KpMakelaars(target_config)
            case 'pararius':
                return Pararius(target_config)
            case 'gruno_verhuur':
                return GrunoVerhuur(target_config)
            case _:
                raise ValueError(target + " is not a valid target, please update the config")


class Monitor:
    interval: int
    targets: list[Target]
    stored: {Target: list[str]}

    def __init__(self, interval, targets, target_config) -> None:
        super().__init__()
        self.interval = interval
        self.targets = [TargetBuilder.build_target(target, target_config) for target in targets]
        self.stored = {target: [] for target in targets}

    def start(self) -> None:
        running = True

        while running:
            results: [Advertisement] = self.run()
            for advertisement in results:
                self._send_notification(advertisement)
                sleep(self.interval)

    def _send_notification(self, advertisement: Advertisement):
        title = "New advertisement found on: {target_name}.".format(
            target_name=advertisement.url
        )

        description = "Price: {price} - Size: {size}".format(
            price=advertisement.price,
            size=advertisement.apartment.size
        )

        print(title + " -- " + description)

        notification = notifypy.Notify()
        notification.title = title
        notification.message = description
        notification.send()

    def run(self) -> [Advertisement]:
        results: [Advertisement] = list()

        for target in self.targets:
            for advertisement in target.get_advertisements():
                if advertisement.url not in self.stored[target.name]:
                    self.stored[target.name].append(advertisement.url)
                    results.append(advertisement)

        return results
