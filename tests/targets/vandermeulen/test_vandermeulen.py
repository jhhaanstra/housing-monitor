import unittest
from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.vandermeulen import (
    Capture,
    VanderMeulen,
    HttpRequestor,
    Requestor,
    SearchExtractor,
)
from targets.target import TargetConfig


class GrunoVerhuurSearchTest(unittest.TestCase):
    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEqual(len(advertisements), 1)
        actual = advertisements[0]
        self.assertEqual(
            actual.url,
            "https://www.vandermeulenmakelaars.nl/huurwoningen/oosterstraat-groningen-h107120464/",
        )
        self.assertEqual(actual.price, "937")
        self.assertEqual(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(
            actual_apartment.address, "Oosterstraat"
        )
        self.assertEqual(actual_apartment.city, "Groningen")
        self.assertEqual(actual_apartment.size, 48)

    @unittest.skip("Live test")
    def test_vandermeulen_live(self):
        config = TargetConfig(500, 1000, 30)
        vandermeulen = VanderMeulen(config, requestor=HttpRequestor())
        advertisements: list[Advertisement] = vandermeulen.get_advertisements()

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
        self.assertEqual(
            "https://www.vandermeulenmakelaars.nl/huurwoningen/?_plaats=groningen&_status=beschikbaar&_prijsbereik=800.00%2C1200.00",
            url,
        )


class TestRequestor(Requestor):
    def request_search_page(self, config: TargetConfig) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text(
        "tests.targets.vandermeulen", "vandermeulen_search_page.html"
    ) as t:
        return Capture(t.read())


if __name__ == "__main__":
    unittest.main()
