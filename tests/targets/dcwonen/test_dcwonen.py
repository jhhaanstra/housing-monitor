import unittest

from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.dcwonen import SearchExtractor, Requestor, Capture, DcWonen, HttpRequestor
from targets.target import TargetConfig


class DcWonenSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEqual(len(advertisements), 5)
        actual = advertisements[0]
        self.assertEqual(actual.url, "https://dcwonen.nl/appartement-5-slaapkamers-werfstraat/")
        self.assertEqual(actual.price, "€2,175/1 juli")
        self.assertEqual(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEqual(actual_apartment.address, "Appartement (5 slaapkamers) Werfstraat")
        self.assertEqual(actual_apartment.city, "Werfstraat, Groningen")

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()
        for advertisement in advertisements:
            self.assertEqual(advertisement.state, AdvertisementState.AVAILABLE)

    @unittest.skip("Live test")
    def test_dc_wonen_live(self):
        config = TargetConfig(500, 1000, 30)
        dc_wonen = DcWonen(config, requestor=HttpRequestor())
        advertisements: list[Advertisement] = dc_wonen.get_advertisements()

        for advertisement in advertisements:
            self.assertIsNotNone(advertisement.url)
            self.assertIsNotNone(advertisement.price)
            self.assertIsNotNone(advertisement.state)

            actual_apartment = advertisement.apartment
            self.assertIsNotNone(actual_apartment.address)
            self.assertIsNotNone(actual_apartment.city)

    def test_use_config_in_url(self):
        config = TargetConfig(800, 1200, 30)
        requestor = HttpRequestor()
        url = requestor.build_search_url(config)
        self.assertEqual("https://dcwonen.nl/zoeken/?type=&min-price=%E2%82%AC800&max-price=%E2%82%AC1,200&min-area=0+m%C2%B2&max-area=500+m%C2%B2", url)


class TestRequestor(Requestor):
    def request_search_page(self, config: TargetConfig) -> Capture:
        return read_capture()


def read_capture() -> Capture:
    with resources.open_text("tests.targets.dcwonen", "dcwonen_search_page.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
