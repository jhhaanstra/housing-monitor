import unittest

from main import Monitor
from model.model import Advertisement, Apartment
from monitor.monitor import TargetBuilder
from targets.dcwonen import DcWonen
from targets.grunoverhuur import GrunoVerhuur
from targets.kpmakelaars import KpMakelaars
from targets.pandomo import Pandomo
from targets.pararius import Pararius
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


class TargetBuilderTest(unittest.TestCase):

    config: TargetConfig = TargetConfig(800, 1200, 40)

    def test_should_build_pandomo(self):
        target: Target = TargetBuilder.build_target('pandomo', self.config)
        self.assertIsInstance(target, Pandomo)
        self.assertEquals(target.name, 'pandomo')
        self.assertEquals(target.config, self.config)

    def test_should_build_dc_wonen(self):
        target: Target = TargetBuilder.build_target('dcwonen', self.config)
        self.assertIsInstance(target, DcWonen)
        self.assertEquals(target.name, 'dcwonen')
        self.assertEquals(target.config, self.config)

    def test_should_build_kp_makelaars(self):
        target: Target = TargetBuilder.build_target('kpmakelaars', self.config)
        self.assertIsInstance(target, KpMakelaars)
        self.assertEquals(target.name, 'kpmakelaars')
        self.assertEquals(target.config, self.config)

    def test_should_build_pararius(self):
        target: Target = TargetBuilder.build_target('pararius', self.config)
        self.assertIsInstance(target, Pararius)
        self.assertEquals(target.name, 'pararius')
        self.assertEquals(target.config, self.config)

    def test_should_build_gruno_verhuur(self):
        target: Target = TargetBuilder.build_target('grunoverhuur', self.config)
        self.assertIsInstance(target, GrunoVerhuur)
        self.assertEquals(target.name, 'grunoverhuur')
        self.assertEquals(target.config, self.config)

    def test_should_throw_value_error_on_invalid_name(self):
        try:
            TargetBuilder.build_target('invalid', self.config)
            self.fail("Should've thrown a ValueError")
        except ValueError:
            pass


class StaticTarget(Target):
    advertisements: list[Advertisement]

    def __init__(self, advertisements: list[Advertisement]) -> None:
        super().__init__(TargetConfig(0, 0, 0), 'static')
        self.advertisements = advertisements

    def get_advertisements(self) -> list[Advertisement]:
        return self.advertisements
