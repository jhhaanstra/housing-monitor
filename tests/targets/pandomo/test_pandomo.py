import unittest
from importlib import resources

import pytest

from model.model import Advertisement, AdvertisementState
from targets.pandomo import Capture, SearchExtractor, Pandomo, Requestor
from targets.target import Config


class PandomoSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEquals(len(advertisements), 12)
        actual = advertisements[0]
        self.assertEquals(actual.url, "https://www.pandomo.nl/huurwoningen/h/stalstraat-8-322875/")
        self.assertEquals(actual.price, "€1.475,00 p.m")
        self.assertEquals(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEquals(actual_apartment.address, "Stalstraat 8")
        self.assertEquals(actual_apartment.postal_code, "9712ES")
        self.assertEquals(actual_apartment.city, "Groningen")
        self.assertEquals(actual_apartment.size, 64)

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()
        self.assertEquals(advertisements[0].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[8].state, AdvertisementState.UNDER_OPTION)
        self.assertEquals(advertisements[11].state, AdvertisementState.UNAVAILABLE)

    @pytest.mark.skip("Live test")
    def test_pandomo_live(self):
        config = Config(1500, 1000, 30)
        pandomo = Pandomo(config, TestRequestor())
        advertisements: list[Advertisement] = pandomo.get_advertisements()

        for advertisement in advertisements:
            self.assertIsNotNone(advertisement.url)
            self.assertIsNotNone(advertisement.price)
            self.assertIsNotNone(advertisement.state)

            actual_apartment = advertisement.apartment
            self.assertIsNotNone(actual_apartment.address)
            self.assertIsNotNone(actual_apartment.postal_code)
            self.assertIsNotNone(actual_apartment.city)
            self.assertIsNotNone(actual_apartment.size)


class TestRequestor(Requestor):
    def request_search_page(self) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text("tests.targets.pandomo", "pandomo_search_page.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
