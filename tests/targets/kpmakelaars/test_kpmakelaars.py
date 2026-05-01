import unittest

from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.kpmakelaars import SearchExtractor, Requestor, Capture, KpMakelaars, HttpRequestor
from targets.target import TargetConfig


class KpMakelaarsSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEqual(len(advertisements), 5)
        actual = advertisements[0]
        self.assertEqual(actual.url, "https://www.kpmakelaars.nl/woning/Groningen-Aweg-H00250255")
        self.assertEqual(actual.price, "€895,- \/mnd (incl)")
        self.assertEqual(actual.state, AdvertisementState.UNAVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(actual_apartment.address, "Aweg 5-307")
        self.assertEqual(actual_apartment.postal_code, "9718CS")
        self.assertEqual(actual_apartment.city, "Groningen")
        self.assertEqual(actual_apartment.size, 26)

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()
        self.assertEqual(advertisements[0].state, AdvertisementState.UNAVAILABLE)
        self.assertEqual(advertisements[1].state, AdvertisementState.AVAILABLE)
        self.assertEqual(advertisements[2].state, AdvertisementState.AVAILABLE)
        self.assertEqual(advertisements[3].state, AdvertisementState.AVAILABLE)
        self.assertEqual(advertisements[4].state, AdvertisementState.AVAILABLE)

    def test_use_config_in_url(self):
        config = TargetConfig(800, 1200, 30)
        requestor = HttpRequestor()
        url = requestor.build_search_query(config)
        self.assertEqual("min_price=800&max_price=1200&min_area=30", url)


    @unittest.skip("Live test")
    def test_kpmakelaars_live(self):
        config = TargetConfig(500, 1000, 30)
        kpmakelaars = KpMakelaars(config, requestor=HttpRequestor())
        advertisements: list[Advertisement] = kpmakelaars.get_advertisements()

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
