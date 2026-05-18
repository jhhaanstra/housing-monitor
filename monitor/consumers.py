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
            f"New advertisement found on: {advertisement.url} -- Price: {advertisement.price} - Size: {advertisement.size}"
        )


class FileWritingConsumer(AdvertisementConsumer):
    def accept(self, advertisement: Advertisement):
        with open("advertisements.txt", "a") as f:
            f.write(advertisement.url + "\n")


class NotifyingConsumer(AdvertisementConsumer):
    def accept(self, advertisement: Advertisement):
        notification = Notify()
        notification.title = f"New advertisement found on: {advertisement.url}."
        notification.message = (
            f"Price: {advertisement.price} - Size: {advertisement.size}"
        )
        notification.send(block=False)
