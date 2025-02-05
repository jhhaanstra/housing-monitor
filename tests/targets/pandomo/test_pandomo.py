import unittest
from importlib import resources

import pytest

from model.model import Advertisement, AdvertisementState
from targets.pandomo import Capture, SearchExtractor, Pandomo, Requestor, HttpRequestor
from targets.target import TargetConfig


class PandomoSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEquals(len(advertisements), 12)
        actual = advertisements[0]
        self.assertEquals(actual.url, "https://www.pandomo.nl/huurwoningen/h/hoogeweg-1-404680/")
        self.assertEquals(actual.price, "€ 950,00 p.m")
        self.assertEquals(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEquals(actual_apartment.address, "Hoogeweg 1")
        self.assertEquals(actual_apartment.postal_code, "9746TN")
        self.assertEquals(actual_apartment.city, "groningen")
        self.assertEquals(actual_apartment.size, 19)

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()
        self.assertEquals(advertisements[0].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[1].state, AdvertisementState.UNDER_OPTION)
        self.assertEquals(advertisements[2].state, AdvertisementState.UNAVAILABLE)

    def test_use_config_in_url(self):
        config = TargetConfig(800, 1200, 30)
        requestor = HttpRequestor()
        url = requestor.build_search_url(config)
        self.assertEquals("https://www.pandomo.nl/huurwoningen/?filter-group-id=10&filter%5B39%5D=800%2C1200&filter[43]=19%2C30", url)

    @pytest.mark.skip("Live test")
    def test_pandomo_live(self):
        config = TargetConfig(500, 1000, 30)
        pandomo = Pandomo(config, requestor=HttpRequestor())
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
    def request_search_page(self, config: TargetConfig) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text("tests.targets.pandomo", "pandomo_search_page.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
