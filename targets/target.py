from abc import abstractmethod, ABC

from model.model import Advertisement


class Config:
    min_price: int
    max_price: int
    min_surface: int

    def __init__(self, min_price, max_price, min_surface) -> None:
        self.min_price = min_price
        self.max_price = max_price
        self.min_surface = min_surface
        super().__init__()


class Target(ABC):
    config: Config

    def __init__(self, config: Config) -> None:
        self.config = config
        super().__init__()

    @abstractmethod
    def get_advertisements(self) -> list[Advertisement]:
        pass
