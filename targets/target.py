from abc import abstractmethod, ABC


class Target(ABC):

    @abstractmethod
    def request(self):
        pass

    @abstractmethod
    def parse(self):
        pass
