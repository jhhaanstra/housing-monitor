from abc import ABC, abstractmethod

import requests
from lxml import html

from model.model import Advertisement, AdvertisementState, Apartment
from targets.target import TargetConfig, Target


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
        response = requests.get(url)
        return Capture(response.content.decode("utf-8"))

    def build_search_url(self, config):
        return "https://www.grunoverhuur.nl/huuraanbod/?search_property=&lang=nl&property_type=&property_area={size}-1000&property_bedrooms=&property_city=Groningen&price_min={min_price}%2C00&price_max={max_price}%2C00".format(
            size=config.min_surface,
            min_price=config.min_price,
            max_price=config.max_price
        )

class SearchExtractor:
    _ADVERTISEMENT_BASE = "//div[preceding-sibling::h4[text()='Beschikbare woningen']]//div[contains(@id, 'property') and not(.//div[contains(@class, 'verhuurd')])]"
    _ADVERTISEMENT_URL = ".//div[@class='footer-buttons']/a"
    _ADVERTISEMENT_PRICE = ".//span[@class='price']"
    _ADVERTISEMENT_SIZE = ".//span[@title='Oppervlakte']"
    _ADVERTISEMENT_CITY = ".//div[@class='category']/span[last()]"
    _ADVERTISEMENT_ADDRESS = ".//span[@class='location']/text()"

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
        advertisement.url = node.xpath(self._ADVERTISEMENT_URL)[0].attrib["href"]
        advertisement.price = "".join(node.xpath(".//span[@class='price']")[0].itertext()).strip()
        advertisement.state = AdvertisementState.AVAILABLE
        advertisement.apartment = self._apartment_from_node(node)
        return advertisement

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()

        apartment.address = node.xpath(self._ADVERTISEMENT_ADDRESS)[0].strip()
        apartment.city = node.xpath(self._ADVERTISEMENT_CITY)[0].text.strip()
        size_text = "".join(node.xpath(self._ADVERTISEMENT_SIZE)[0].itertext()).strip()
        apartment.size = int(size_text.split(" ")[0])

        return apartment


class GrunoVerhuur(Target):

    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, 'grunoverhuur')
        if 'requestor' in kwargs:
            self.requestor = kwargs['requestor']
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page(self.config)
        extractor = SearchExtractor(capture)
        return extractor.get_advertisements()
