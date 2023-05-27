import requests
from lxml import html

from model.model import Advertisement
from targets.target import Target


class Pandomo(Target):

    def request(self):
        return requests.get('http://example.org/')

    def parse(self, capture) -> list[Advertisement]:
        return []


class Capture:

    content: html.HtmlElement

    def __init__(self, content: str) -> None:
        super().__init__()
        self.content = html.fromstring(content)


class Extractor:
    capture: Capture

    def __init__(self, capture: Capture) -> None:
        super().__init__()
        self.capture = capture

    def get_advertisements(self) -> list[Advertisement]:
        return []

    def get_nr_advertisements(self):
        return len(self.capture.content.xpath("//li[@class='results__item']"))