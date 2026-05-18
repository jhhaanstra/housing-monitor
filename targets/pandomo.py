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
    def request_search_page(self, config: TargetConfig) -> Capture:
        pass


class HttpRequestor(Requestor):
    def request_search_page(self, config: TargetConfig) -> Capture:
        url = self.build_search_url(config)
        response = requests.get(url, timeout=5)
        return Capture(response.content.decode("utf-8"))

    def build_search_url(self, config):
        return "https://www.pandomo.nl/wonen/huur?weergave=grid&soort=&plaats=Groningen&prijs=&oppervlakte={min_surface}".format(
            min_surface=config.min_surface,
        )


class SearchExtractor:
    BASE_URL = "https://www.pandomo.nl"

    _ADVERTISEMENT_BASE = "//a[@class='card card--offer']"
    _ADVERTISEMENT_POSTAL_CODE = ".//p[@class='card-offer_subtitle']"
    _ADVERTISEMENT_URL = ".//h3/a"
    _ADVERTISEMENT_DESCRIPTION = "./div/p"
    _ADVERTISEMENT_PRICE = ".//div[@class='card-offer__price']"
    _ADVERTISEMENT_LABEL = "./a/div/*[contains(@class, 'image__label')]"
    _ADVERTISEMENT_SURFACE = ".//div[@class='card-offer__bottom']/ul/li[1]/text()"

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
        advertisement = Advertisement()
        advertisement.url = node.attrib["href"]
        advertisement.price = self._price_from_node(node)
        advertisement.state = AdvertisementState.AVAILABLE
        advertisement.apartment = self._apartment_from_node(node)
        return advertisement

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()
        apartment.address = node.attrib["title"]
        apartment.postal_code = node.xpath(self._ADVERTISEMENT_POSTAL_CODE)[0].text
        apartment.city = "Groningen"
        apartment.size = int(
            node.xpath(self._ADVERTISEMENT_SURFACE)[1].strip().split(" ")[0]
        )
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


class Pandomo(Target):
    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, "pandomo")
        if "requestor" in kwargs:
            self.requestor = kwargs["requestor"]
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page(self.config)
        extractor = SearchExtractor(capture)
        return [
            a
            for a in extractor.get_advertisements()
            if float(a.price) <= self.config.max_price
            and float(a.price) >= self.config.min_price
        ]
