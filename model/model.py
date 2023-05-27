from datetime import date, datetime


class Apartment:
    address: str
    size: int  # In m2


class Advertisement:
    url: str
    created_at: date
    fetched: datetime
