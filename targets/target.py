from abc import abstractmethod, ABC

from model.model import Advertisement


class TargetConfig:
    min_price: int
    max_price: int
    min_surface: int

    def __init__(self, min_price, max_price, min_surface) -> None:
        super().__init__()
        self.min_price = min_price
        self.max_price = max_price
        self.min_surface = min_surface


class Target(ABC):

    config: TargetConfig
    name: str

    def __init__(self, config: TargetConfig, name: str) -> None:
        super().__init__()
        self.config = config
        self.name = name

    @abstractmethod
    def get_advertisements(self) -> list[Advertisement]:
        pass
