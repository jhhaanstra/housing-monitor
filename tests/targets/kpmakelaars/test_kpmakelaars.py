import unittest
import pytest

from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.kpmakelaars import SearchExtractor, Requestor, Capture, KpMakelaars
from targets.target import TargetConfig


class KpMakelaarsSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEquals(len(advertisements), 5)
        actual = advertisements[0]
        self.assertEquals(actual.url, "https://www.kpmakelaars.nl/woning?Groningen/Aweg/H00250255")
        self.assertEquals(actual.price, "€895,- \/mnd (incl)")
        self.assertEquals(actual.state, AdvertisementState.UNAVAILABLE)

        actual_apartment = actual.apartment
        self.assertEquals(actual_apartment.address, "Aweg 5-307")
        self.assertEquals(actual_apartment.postal_code, "9718CS")
        self.assertEquals(actual_apartment.city, "Groningen")
        self.assertEquals(actual_apartment.size, 26)

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()
        self.assertEquals(advertisements[0].state, AdvertisementState.UNAVAILABLE)
        self.assertEquals(advertisements[1].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[2].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[3].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[4].state, AdvertisementState.AVAILABLE)

    @pytest.mark.skip("Live test")
    def test_pararius_live(self):
        config = TargetConfig(1400, 1000, 30)
        pararius = KpMakelaars(config, requestor=TestRequestor())
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
    with resources.open_text("tests.targets.kpmakelaars", "kpmakelaars_search_page.json") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
