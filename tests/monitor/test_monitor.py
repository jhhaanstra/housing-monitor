import unittest

from model.model import Advertisement, Apartment
from main import Monitor
from targets.target import Target, TargetConfig


class MonitorTest(unittest.TestCase):

    def test_should_get_advertisements(self):
        apartment = Apartment()
        apartment.size = 100
        apartment.city = "Amsterdam"

        advertisement = Advertisement()
        advertisement.url = "foo.bar"
        advertisement.price = 123.45
        advertisement.apartment = apartment

        apartment2 = Apartment()
        apartment2.size = 200
        apartment2.city = "Groningen"

        advertisement2 = Advertisement()
        advertisement2.url = "bar.baz"
        advertisement2.price = 12.65
        advertisement2.apartment = apartment2

        static_target = StaticTarget([advertisement, advertisement2])

        monitor = Monitor(1, [], TargetConfig(1, 2, 3))
        monitor.targets = [static_target]
        monitor.stored = {'static': []}

        run1 = monitor.run()
        self.assertListEqual(run1, [advertisement, advertisement2])

        run2 = monitor.run()
        self.assertListEqual(run2, [])


class StaticTarget(Target):
    advertisements: list[Advertisement]

    def __init__(self, advertisements: list[Advertisement]) -> None:
        super().__init__(TargetConfig(0, 0, 0), 'static')
        self.advertisements = advertisements

    def get_advertisements(self) -> list[Advertisement]:
        return self.advertisements
