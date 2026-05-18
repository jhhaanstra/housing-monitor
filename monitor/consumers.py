import logging
from abc import ABC, abstractmethod

import pync

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
        pync.notify(f"Price: {advertisement.price} - Size: {advertisement.size}", title=f"New advertisement found on: {advertisement.url}.")
