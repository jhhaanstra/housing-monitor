import logging
from time import sleep

from requests import ReadTimeout

from model.model import Advertisement
from monitor.consumers import (
    AdvertisementConsumer,
    FileWritingConsumer,
    LoggingConsumer,
    NotifyingConsumer,
)
from targets.dcwonen import DcWonen
from targets.grunoverhuur import GrunoVerhuur
from targets.kpmakelaars import KpMakelaars
from targets.pandomo import Pandomo
from targets.pararius import Pararius
from targets.eentweedriewonen import EenTweeDrieWonen
from targets.target import Target, TargetConfig


class TargetBuilder:
    @staticmethod
    def build_target(target: str, target_config: TargetConfig) -> Target:
        match target.lower():
            case "pandomo":
                return Pandomo(target_config)
            case "dcwonen":
                return DcWonen(target_config)
            case "kpmakelaars":
                return KpMakelaars(target_config)
            case "pararius":
                return Pararius(target_config)
            case "grunoverhuur":
                return GrunoVerhuur(target_config)
            case "123wonen":
                return EenTweeDrieWonen(target_config)
            case _:
                raise ValueError(
                    target + " is not a valid target, please update the config"
                )


class Monitor:
    interval: int
    targets: list[Target]
    stored: list[str]
    consumers: list[AdvertisementConsumer] = [
        LoggingConsumer(),
        FileWritingConsumer(),
        NotifyingConsumer(),
    ]

    def __init__(self, interval, targets, target_config) -> None:
        super().__init__()
        self.interval = interval
        self.targets: list[Target] = [
            TargetBuilder.build_target(target, target_config) for target in targets
        ]
        self.stored = []

    def start(self) -> None:
        running = True

        while running:
            results: list[Advertisement] = self.run()
            for advertisement in results:
                for consumer in self.consumers:
                    consumer.accept(advertisement)

            sleep(self.interval)

    def run(self) -> list[Advertisement]:
        results: list[Advertisement] = list()

        for target in self.targets:
            logging.info(f"fetching target: {target.name}")
            try:
                advertisements = target.get_advertisements()
                logging.info(
                    f"extracted {len(advertisements)} advertisement{('s' * (len(advertisements) != 1))} for target: {target.name}"
                )
                for advertisement in advertisements:
                    if advertisement.url not in self.stored:
                        self.stored.append(advertisement.url)
                        results.append(advertisement)
            except ReadTimeout:
                logging.error(f"Could not fetch target {target.name!r} in time.")
            except Exception as e:
                logging.error(f"Something went wrong fetching target: {target.name!r}", e)

        return results
