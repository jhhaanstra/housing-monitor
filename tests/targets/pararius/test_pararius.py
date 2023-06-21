import unittest
from importlib import resources

from model.model import Advertisement, AdvertisementState
from targets.pararius import SearchExtractor, Requestor, Capture, Pararius
from targets.target import TargetConfig


class ParariusSearchTest(unittest.TestCase):

    def test_should_get_available_advertisement(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()

        self.assertEquals(len(advertisements), 13)
        actual = advertisements[0]
        self.assertEquals(actual.url, "https://www.pararius.com/apartment-for-rent/groningen/fed24a60/pelsterstraat")
        self.assertEquals(actual.price, "€1,000 per month")
        self.assertEquals(actual.state, AdvertisementState.AVAILABLE)

        actual_apartment = actual.apartment
        self.assertEquals(actual_apartment.address, "Flat Pelsterstraat")
        self.assertEquals(actual_apartment.postal_code, "9711KM")
        self.assertEquals(actual_apartment.city, "Groningen (binnenstad-zuid)")
        self.assertEquals(actual_apartment.size, 47)

    def test_should_get_states(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements: list[Advertisement] = extractor.get_advertisements()
        self.assertEquals(advertisements[0].state, AdvertisementState.AVAILABLE)
        self.assertEquals(advertisements[6].state, AdvertisementState.UNAVAILABLE)

    # @pytest.mark.skip("Live test")
    def test_pararius_live(self):
        config = TargetConfig(1400, 1000, 30)
        pararius = Pararius(config, requestor=TestRequestor())
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
    with resources.open_text("tests.targets.pararius", "pararius_search_page.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
