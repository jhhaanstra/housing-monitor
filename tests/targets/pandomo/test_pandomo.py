import unittest
from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.pandomo import Capture, HttpRequestor, Pandomo, Requestor, SearchExtractor
from targets.target import TargetConfig


class PandomoSearchTest(unittest.TestCase):
    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEqual(len(advertisements), 14)
        actual = advertisements[0]
        self.assertEqual(
            actual.url, "https://www.pandomo.nl/wonen/object/stalstraat-66-groningen/"
        )
        self.assertEqual(actual.price, "2200.")
        self.assertEqual(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(actual_apartment.address, "Stalstraat 66")
        self.assertEqual(actual_apartment.postal_code, "9712 ES Groningen")
        self.assertEqual(actual_apartment.city, "Groningen")
        self.assertEqual(actual_apartment.size, 81)

    def test_use_config_in_url(self):
        config = TargetConfig(800, 1200, 30)
        requestor = HttpRequestor()
        url = requestor.build_search_url(config)
        self.assertEqual(
            "https://www.pandomo.nl/wonen/huur?weergave=grid&soort=&plaats=Groningen&prijs=&oppervlakte=30",
            url,
        )


class PandomoTest(unittest.TestCase):
    def test_should_filter_values_undesired_prices(self):
        config = TargetConfig(2190, 3000, 30)
        pandomo = Pandomo(config, requestor=TestRequestor())
        prices = [advertisement.price for advertisement in pandomo.get_advertisements()]
        self.assertEqual(["2200.", "2900.", "2195."], prices)

    @unittest.skip("Live test")
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


if __name__ == "__main__":
    unittest.main()
