import re
from abc import ABC, abstractmethod

import requests
from lxml import html

from model.model import Advertisement, AdvertisementState, Apartment
from targets.target import Target, TargetConfig


class Capture:
    raw: str
    content: html.HtmlElement

    def __init__(self, content: str) -> None:
        super().__init__()
        self.raw = content
        self.content = html.fromstring(content)


class Requestor(ABC):
    @abstractmethod
    def request_search_page(self) -> Capture:
        pass


class HttpRequestor(Requestor):
    def request_search_page(self) -> Capture:
        url = self.build_search_url()
        response = requests.get(url, timeout=15)
        return Capture(response.content.decode("utf-8"))

    def build_search_url(self, page: int = 1) -> str:
        return f"https://dcwonen.nl/verhuur/page/{page}"


class SearchExtractor:
    _ADVERTISEMENT_BASE = "//li[@class='item']"
    _ADVERTISEMENT_TITLE_URL = "./a"
    _ADVERTISEMENT_ADDRESS = "./a//span[@class='object-name']"
    _ADVERTISEMENT_CITY = "./a//span[@class='object-address']"
    _ADVERTISEMENT_PRICE = "./a//span[@class='object-price']"

    capture: Capture

    def __init__(self, capture: Capture) -> None:
        super().__init__()
        self.capture = capture

    def get_advertisements(self) -> list[Advertisement]:
        nodes = self.capture.content.xpath(self._ADVERTISEMENT_BASE)
        results = []

        for node in nodes:
            results.append(self._advertisement_from_node(node))

        return results

    def _advertisement_from_node(self, node: html.HtmlElement) -> Advertisement:
        elements: list[html.HtmlElement] = node.xpath(self._ADVERTISEMENT_TITLE_URL)
        if len(elements) == 0:
            raise ValueError("Invalid advertisement node provided")
        else:
            title = node.xpath(self._ADVERTISEMENT_TITLE_URL)[0]
            advertisement = Advertisement()
            advertisement.url = title.attrib["href"]
            advertisement.price = self._price_from_node(node)
            advertisement.state = AdvertisementState.AVAILABLE
            advertisement.apartment = self._apartment_from_node(node)
            return advertisement

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()
        apartment.address = node.xpath(self._ADVERTISEMENT_ADDRESS)[0].text.strip()
        apartment.city = node.xpath(self._ADVERTISEMENT_CITY)[0].text.strip()
        return apartment

    def _price_from_node(self, node: html.HtmlElement) -> str:
        node_text = node.xpath(self._ADVERTISEMENT_PRICE)[0].text
        # Extract the first number-like pattern
        match = re.search(r"([\d.,]+)", node_text)
        if match:
            value_str = match.group(1)  # "750,00"
            return value_str.replace(".", "").replace(",", ".")
        else:
            raise ValueError(f"invalid price found {node_text}")


class DcWonen(Target):
    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, "dcwonen")
        if "requestor" in kwargs:
            self.requestor = kwargs["requestor"]
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page()
        extractor = SearchExtractor(capture)
        return [
            a
            for a in extractor.get_advertisements()
            if float(a.price) <= self.config.max_price
            and float(a.price) >= self.config.min_price
        ]
