import unittest

from importlib import resources

from targets.pandomo import Capture, Extractor


class PandomoCaptureParsingTest(unittest.TestCase):

    def test_should_get_advertisements(self):
        capture = read_capture()
        extractor = Extractor(capture)
        self.assertEquals(extractor.get_nr_advertisements(), 12)


def read_capture() -> Capture:
    with resources.open_text("tests.targets", "pandomo_capture.html") as t:
        return Capture(t.read())


if __name__ == '__main__':
    unittest.main()
