import unittest
import pytest

from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.grunoverhuur import SearchExtractor, Requestor, Capture, GrunoVerhuur, HttpRequestor
from targets.target import TargetConfig


class GrunoVerhuurSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEquals(len(advertisements), 10)
        actual = advertisements[0]
        self.assertEquals(actual.url, "https://www.grunoverhuur.nl/woningaanbod/huur/groningen/oosterweg/30-b")
        self.assertEquals(actual.price, "€ 785,- /mnd")
        self.assertEquals(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEquals(actual_apartment.address, "Oosterweg 30B, 9724CJ Groningen")
        self.assertEquals(actual_apartment.city, "Groningen (probably)")
        self.assertEquals(actual_apartment.size, 29)

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEquals(advertisements[0].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[2].state, AdvertisementState.AVAILABLE)

    # @pytest.mark.skip("Live test")
    def test_gruno_verhuur_live(self):
        config = TargetConfig(500, 1000, 30)
        gruno_verhuur = GrunoVerhuur(config, requestor=HttpRequestor())
        advertisements: list[Advertisement] = gruno_verhuur.get_advertisements()

        for advertisement in advertisements:
            self.assertIsNotNone(advertisement.url)
            self.assertIsNotNone(advertisement.price)
            self.assertIsNotNone(advertisement.state)

            actual_apartment = advertisement.apartment
            self.assertIsNotNone(actual_apartment.address)
            self.assertIsNotNone(actual_apartment.city)
            self.assertIsNotNone(actual_apartment.size)

    def test_use_config_in_url(self):
        config = TargetConfig(800, 1200, 30)
        requestor = HttpRequestor()
        url = requestor.build_search_url(config)
        self.assertEquals("https://www.grunoverhuur.nl/woningaanbod/huur?moveunavailablelistingstothebottom=true&pricerange.maxprice=1200&pricerange.minprice=800", url)


class TestRequestor(Requestor):
    def request_search_page(self, config: TargetConfig) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text("tests.targets.grunoverhuur", "gruno_verhuur_search_page.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
