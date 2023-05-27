from datetime import datetime


class Apartment:
    address: str
    postal_code: str
    city: str
    size: int  # In m2
    energy: str

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Apartment):
            return False

        return self.address == o.address and \
            self.postal_code == o.postal_code and \
            self.city == o.city and \
            self.size == o.size and \
            self.energy == o.energy


class Advertisement:
    url: str
    apartment: Apartment
    price: float
    date_fetched: datetime

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Advertisement):
            return False

        return self.url == o.url and \
            self.apartment == o.apartment and \
            self.price == o.price and \
            self.date_fetched == o.date_fetched
