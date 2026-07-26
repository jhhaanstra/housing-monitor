import unittest
from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.dcwonen import (
    Capture,
    DcWonen,
    HttpRequestor,
    Requestor,
    SearchExtractor,
)
from targets.target import TargetConfig


class DcWonenSearchTest(unittest.TestCase):
    def test_should_get_available_advertisement(self):
        capture: Capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEqual(len(advertisements), 5)
        actual = advertisements[0]
        self.assertEqual(actual.url, "https://dcwonen.nl/verhuur/j-a-feithstraat-2")
        self.assertEqual(actual.price, "750")
        self.assertEqual(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(actual_apartment.address, "J.A. Feithstraat")
        self.assertEqual(actual_apartment.city, "Groningen")

    @unittest.skip("Live test")
    def test_dc_wonen_live(self):
        config = TargetConfig(500, 2000, 30)
        dc_wonen = DcWonen(config, requestor=HttpRequestor())
        advertisements: list[Advertisement] = dc_wonen.get_advertisements()

        for advertisement in advertisements:
            self.assertIsNotNone(advertisement.url)
            self.assertIsNotNone(advertisement.price)
            self.assertIsNotNone(advertisement.state)

            actual_apartment = advertisement.apartment
            self.assertIsNotNone(actual_apartment.address)
            self.assertIsNotNone(actual_apartment.city)


class TestDcWonen(unittest.TestCase):
    def test_should_filter_values_undesired_prices(self):
        config = TargetConfig(500, 1300, 30)
        dc_wonen = DcWonen(config, requestor=TestRequestor())
        prices = [
            advertisement.price for advertisement in dc_wonen.get_advertisements()
        ]
        self.assertEqual(["750", "628", "1255"], prices)


class TestRequestor(Requestor):
    def request_search_page(self) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text("tests.targets.dcwonen", "dcwonen_search_page.html") as t:
        return Capture(t.read())


if __name__ == "__main__":
    unittest.main()
