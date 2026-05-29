import logging
from abc import ABC, abstractmethod

from notifypy import Notify

from model.model import Advertisement


class AdvertisementConsumer(ABC):
    @abstractmethod
    def accept(self, advertisement: Advertisement):
        pass


class LoggingConsumer(AdvertisementConsumer):
    def accept(self, advertisement: Advertisement):
        logging.info(
            f"New advertisement found: price: €{advertisement.price:>4} - size: {advertisement.apartment.size:>3}m² -- {advertisement.url}"
        )


class FileWritingConsumer(AdvertisementConsumer):
    def accept(self, advertisement: Advertisement):
        with open("advertisements.txt", "a") as f:
            f.write(advertisement.url + "\n")


class NotifyingConsumer(AdvertisementConsumer):
    def accept(self, advertisement: Advertisement):
        notification = Notify()
        notification.application_name = "Housing monitor"
        notification.title = f"New: {advertisement.apartment.address}"
        notification.message = (
            f"Price: {advertisement.price} - Size: {advertisement.apartment.size}\n"
            f"{advertisement.url}"
        )
        notification.icon = "monitor/monitor.png"
        notification.send(block=False)
