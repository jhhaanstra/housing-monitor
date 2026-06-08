import unittest
from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.eentweedriewonen import (
    Capture,
    EenTweeDrieWonen,
    HttpRequestor,
    Requestor,
    SearchExtractor,
)
from targets.target import TargetConfig


class EenTweeDrieWonenSearchTest(unittest.TestCase):
    def test_should_get_available_advertisement(self):
        capture: Capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEqual(len(advertisements), 3)
        actual = advertisements[0]
        self.assertEqual(actual.url, "https://www.123wonen.nl/huur/groningen/benedenwoning/bordewijklaan-5358-2")
        self.assertEqual(actual.price, "1110")
        self.assertEqual(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(actual_apartment.address, "Bordewijklaan")
        self.assertEqual(actual_apartment.city, "Groningen")

    @unittest.skip("Live test")
    def test_eentweedrie_wonen_live(self):
        config = TargetConfig(700, 2000, 30)
        eentweedrie_wonen = EenTweeDrieWonen(config, requestor=HttpRequestor())
        advertisements: list[Advertisement] = eentweedrie_wonen.get_advertisements()

        for advertisement in advertisements:
            self.assertIsNotNone(advertisement.url)
            self.assertIsNotNone(advertisement.price)
            self.assertIsNotNone(advertisement.state)

            actual_apartment = advertisement.apartment
            self.assertIsNotNone(actual_apartment.address)
            self.assertIsNotNone(actual_apartment.city)


class TestEenTweeDrieWonen(unittest.TestCase):
    def test_should_filter_values_undesired_prices(self):
        config = TargetConfig(500, 1300, 30)
        eentweedrie_wonen = EenTweeDrieWonen(config, requestor=TestRequestor())
        prices = [
            advertisement.price for advertisement in eentweedrie_wonen.get_advertisements()
        ]
        self.assertEqual(["1110", "1097", "1077"], prices)


class TestRequestor(Requestor):
    def request_search_page(self, config: TargetConfig) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text("tests.targets.eentweedriewonen", "eentweedriewonen_search_page.html") as t:
        return Capture(t.read())


if __name__ == "__main__":
    unittest.main()
