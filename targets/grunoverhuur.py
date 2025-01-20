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
        return "https://www.grunoverhuur.nl/woningaanbod/huur?moveunavailablelistingstothebottom=true&pricerange.maxprice={max_price}&pricerange.minprice={min_price}".format(
            min_price=config.min_price,
            max_price=config.max_price
        )

class SearchExtractor:
    _ADVERTISEMENT_BASE = "//article//div[@class='datacontainer']"
    _ADVERTISEMENT_URL = "./a"
    _ADVERTISEMENT_PRICE = "./a//span[@class='obj_price']/text()"
    _ADVERTISEMENT_SIZE = "./a//span[@title='Woonoppervlakte']/text()"
    _ADVERTISEMENT_ADDRESS = "./a//h3/text()"
    _BASE_URL = "https://www.grunoverhuur.nl"

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
        advertisement.url = self._extract_url(node)
        advertisement.price = node.xpath(self._ADVERTISEMENT_PRICE)[0].strip()
        advertisement.state = AdvertisementState.AVAILABLE
        advertisement.apartment = self._apartment_from_node(node)
        return advertisement

    def _extract_url(self, node: html.HtmlElement) -> str:
        url: str = node.xpath(self._ADVERTISEMENT_URL)[0].attrib["href"]
        url = url.split("?")[0]
        return self._BASE_URL + url


    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()

        apartment.address = node.xpath(self._ADVERTISEMENT_ADDRESS)[0].strip().replace("Te huur: ", "")
        apartment.city = "Groningen (probably)"
        size_text = node.xpath(self._ADVERTISEMENT_SIZE)[0].strip()
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
