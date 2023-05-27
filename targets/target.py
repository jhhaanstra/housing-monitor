from abc import abstractmethod, ABC

from model.model import Advertisement


class Target(ABC):

    @abstractmethod
    def request(self):
        pass

    @abstractmethod
    def parse(self, capture) -> list[Advertisement]:
        pass
