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
        # url = "https://dcwonen.nl/zoeken/?type=&min-price=%E2%82%AC{min_price}&max-price=%E2%82%AC{max_price}&min-area={size}+m%C2%B2".format(
        #     max_price=self._format_number(config.max_price),
        #     min_price=self._format_number(config.min_price),
        #     size=config.min_surface
        # )
        response = requests.get("https://dcwonen.nl/te-huur/")
        return Capture(response.content.decode("utf-8"))

    def _format_number(self, nr: int) -> str:
        return f'{nr:,}'


class SearchExtractor:
    _ADVERTISEMENT_BASE = "//div[contains(@class, 'property-listing')]/div[@class='row']/div"
    _ADVERTISEMENT_TITLE_URL = ".//h2/a"
    _ADVERTISEMENT_ADDRESS = ".//address"
    _ADVERTISEMENT_PRICE = "./div/div[2]//span[@class='item-price']"
    _ADVERTISEMENT_LABEL = "./div/div[2]//span[1][contains(@class, 'label')]/a"

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
            advertisement.price = node.xpath(self._ADVERTISEMENT_PRICE)[0].text.strip()
            advertisement.state = self._state_from_node(node)
            advertisement.apartment = self._apartment_from_node(node)
            return advertisement

    def _state_from_node(self, node: html.HtmlElement) -> AdvertisementState:
        labels = node.xpath(self._ADVERTISEMENT_LABEL)
        if not labels:
            return AdvertisementState.AVAILABLE

        label: str = labels[0].text.lower().strip()

        match label:
            case "te huur":
                return AdvertisementState.AVAILABLE
            case _:
                return AdvertisementState.UNAVAILABLE

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()

        title = node.xpath(self._ADVERTISEMENT_TITLE_URL)[0]
        apartment.address = title.text.strip()
        apartment.city = node.xpath(self._ADVERTISEMENT_ADDRESS)[0].text.strip()

        return apartment


class DcWonen(Target):

    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, 'dcwonen')
        if 'requestor' in kwargs:
            self.requestor = kwargs['requestor']
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page(self.config)
        extractor = SearchExtractor(capture)
        return extractor.get_advertisements()
