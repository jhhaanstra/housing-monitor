import uuid
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class AdvertisementState(Enum):
    AVAILABLE = 1
    UNDER_OPTION = 2
    UNAVAILABLE = 3


class Apartment:
    address: str
    postal_code: str
    city: str
    size: int  # In m2

    def __getattr__(self, name: str) -> Any:
        return None

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Apartment):
            return False

        return self.address == o.address and \
            self.postal_code == o.postal_code and \
            self.city == o.city and \
            self.size == o.size


class Advertisement:

    url: str
    apartment: Apartment
    price: str
    date_fetched: datetime
    state: AdvertisementState

    def __getattr__(self, name: str) -> Any:
        return None

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Advertisement):
            return False

        return self.url == o.url and \
            self.apartment == o.apartment and \
            self.price == o.price and \
            self.date_fetched == o.date_fetched and \
            self.state == o.state
