import unittest
from importlib import resources

from targets.pandomo import Capture, SearchExtractor


class PandomoCaptureParsingTest(unittest.TestCase):

    def test_should_get_nr_advertisements(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        self.assertEquals(extractor.get_nr_advertisements(), 12)

    def test_should_get_advertisements(self):
        capture = read_capture()
        extractor = SearchExtractor(capture)
        advertisements = extractor.get_advertisements()

        self.assertEquals(len(advertisements), 12)
        actual = advertisements[0]
        self.assertEquals(actual.url, "https://www.pandomo.nl/huurwoningen/h/lingestraat-47-314029/")
        self.assertEquals(actual.price, 795.00)

        actual_apartment = actual.apartment
        self.assertEquals(actual_apartment.address, "Lingestraat 47")
        self.assertEquals(actual_apartment.postal_code, "9725GN")
        self.assertEquals(actual_apartment.city, "Groningen")
        self.assertEquals(actual_apartment.size, 78)


def read_capture() -> Capture:
    with resources.open_text("tests.targets", "pandomo_capture.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
