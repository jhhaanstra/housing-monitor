import unittest
import pytest

from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.pararius import SearchExtractor, Requestor, Capture, Pararius, HttpRequestor
from targets.target import TargetConfig


class ParariusSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEquals(len(advertisements), 13)
        actual = advertisements[0]
        self.assertEquals(actual.url, "https://www.pararius.com/apartment-for-rent/groningen/cfbcf80e/nieuweweg")
        self.assertEquals(actual.price, "€1,075 per month")
        self.assertEquals(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEquals(actual_apartment.address, "Flat Nieuweweg")
        self.assertEquals(actual_apartment.postal_code, "9711TC")
        self.assertEquals(actual_apartment.city, "Groningen (binnenstad-oost)")
        self.assertEquals(actual_apartment.size, 32)

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()
        self.assertEquals(advertisements[0].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[4].state, AdvertisementState.UNAVAILABLE)

    def test_use_config_in_url(self):
        config = TargetConfig(800, 1200, 30)
        requestor = HttpRequestor()
        url = requestor.build_search_url(config)
        self.assertEquals("https://www.pararius.com/apartments/groningen/800-1200/30m2", url)


    @pytest.mark.skip("Live test")
    def test_pararius_live(self):
        config = TargetConfig(1000, 1400, 30)
        pararius = Pararius(config, requestor=HttpRequestor())
        advertisements: list[Advertisement] = pararius.get_advertisements()

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
    with resources.open_text("tests.targets.pararius", "pararius_search_page.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
