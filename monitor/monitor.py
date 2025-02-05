from time import sleep

from notifypy import Notify

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
            case 'grunoverhuur':
                return GrunoVerhuur(target_config)
            case _:
                raise ValueError(target + " is not a valid target, please update the config")


class Monitor:
    interval: int
    targets: list[Target]
    stored: list[str]

    def __init__(self, interval, targets, target_config) -> None:
        super().__init__()
        self.interval = interval
        self.targets = [TargetBuilder.build_target(target, target_config) for target in targets]
        self.stored = []

    def start(self) -> None:
        running = True

        while running:
            results: [Advertisement] = self.run()
            for advertisement in results:
                self._send_notification(advertisement)
                with open("advertisements.txt", "a") as f:
                    f.write(advertisement.url)
                sleep(self.interval)

    @staticmethod
    def _send_notification(advertisement: Advertisement):
        title = "New advertisement found on: {target_name}.".format(
            target_name=advertisement.url
        )

        description = "Price: {price} - Size: {size}".format(
            price=advertisement.price,
            size=advertisement.apartment.size
        )

        print(title + " -- " + description)

        notification = Notify()
        notification.title = title
        notification.message = description
        notification.send()

    def run(self) -> [Advertisement]:
        results: [Advertisement] = list()

        for target in self.targets:
            for advertisement in target.get_advertisements():
                if advertisement.url not in self.stored:
                    self.stored.append(advertisement.url)
                    results.append(advertisement)

        return results
