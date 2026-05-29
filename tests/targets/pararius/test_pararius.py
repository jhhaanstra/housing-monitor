import unittest
from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.pararius import (
    Capture,
    HttpRequestor,
    Pararius,
    Requestor,
    SearchExtractor,
)
from targets.target import TargetConfig


class ParariusSearchTest(unittest.TestCase):
    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEqual(len(advertisements), 30)
        actual = advertisements[0]
        self.assertEqual(
            actual.url,
            "https://www.pararius.com/huis-te-huur/groningen/7f8c895d/woonschepenhaven",
        )
        self.assertEqual(actual.price, "1000")
        self.assertEqual(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(actual_apartment.address, "Huis Woonschepenhaven")
        self.assertEqual(actual_apartment.postal_code, "9723CJ")
        self.assertEqual(actual_apartment.city, "Groningen (woonschepenhaven)")
        self.assertEqual(actual_apartment.size, 55)

    def test_use_config_in_url(self):
        config = TargetConfig(800, 1200, 30)
        requestor = HttpRequestor()
        url = requestor.build_search_url(config)
        self.assertEqual(
            "https://www.pararius.nl/huurwoningen/groningen/800-1200/30m2", url
        )

    @unittest.skip("Live test")
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
    with resources.open_text(
        "tests.targets.pararius", "pararius_search_page.html"
    ) as t:
        return Capture(t.read())


if __name__ == "__main__":
    unittest.main()
