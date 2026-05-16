import unittest
from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.grunoverhuur import (
    Capture,
    GrunoVerhuur,
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

        self.assertEqual(len(advertisements), 2)
        actual = advertisements[0]
        self.assertEqual(
            actual.url,
            "https://www.grunoverhuur.nl/woningaanbod/huur/groningen/tweede-willemstraat/8-c",
        )
        self.assertEqual(actual.price, "€ 1.157,07 /mnd")
        self.assertEqual(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(
            actual_apartment.address, "Tweede Willemstraat 8C, 9725JJ Groningen"
        )
        self.assertEqual(actual_apartment.city, "Groningen")
        self.assertEqual(actual_apartment.size, 44)

    @unittest.skip("Live test")
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
        self.assertEqual(
            "https://www.grunoverhuur.nl/woningaanbod/huur/groningen?locationofinterest=Groningen&minlivablearea=30&pricerange.maxprice=1200&pricerange.minprice=800",
            url,
        )


class TestRequestor(Requestor):
    def request_search_page(self, config: TargetConfig) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text(
        "tests.targets.grunoverhuur", "gruno_verhuur_search_page.html"
    ) as t:
        return Capture(t.read())


if __name__ == "__main__":
    unittest.main()
