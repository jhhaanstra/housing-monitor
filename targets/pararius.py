from abc import abstractmethod, ABC

import requests
from lxml import html

from model.model import Advertisement, Apartment, AdvertisementState
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
        response = requests.get(url)
        return Capture(response.content.decode("utf-8"))

    def build_search_url(self, config: TargetConfig) -> str:
        return "https://www.pararius.com/apartments/groningen/{min_price}-{max_price}/{size}m2".format(
            min_price=config.min_price,
            max_price=config.max_price,
            size=config.min_surface
        )


class SearchExtractor:
    BASE_URL = "https://www.pararius.com"
    _ADVERTISEMENT_BASE = "//ul[@class='search-list']/li/section"
    _ADVERTISEMENT_TITLE_URL = "./h2/a"
    _ADVERTISEMENT_DESCRIPTION = "./div[contains(@class, 'sub-title')]"
    _ADVERTISEMENT_PRICE = "./div[contains(@class, 'price')]"
    _ADVERTISEMENT_LABEL = "./div[contains(@class, 'label')]/span"
    _ADVERTISEMENT_SPECS = "./div[contains(@class, 'features')]/ul/li[contains(@class, 'surface')]"

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
            advertisement.url = self.BASE_URL + title.attrib["href"]
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
            case "rented under option":
                return AdvertisementState.UNAVAILABLE
            case _:
                return AdvertisementState.AVAILABLE

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()
        description: str = node.xpath(self._ADVERTISEMENT_DESCRIPTION)[0].text.strip()
        split: [str] = description.split(" ")

        title = node.xpath(self._ADVERTISEMENT_TITLE_URL)[0]
        apartment.address = title.text.strip()
        apartment.postal_code = str.join("", split[0:2])

        apartment.city = str.strip(str.join(" ", split[2::]).capitalize())
        apartment.size = int(node.xpath(self._ADVERTISEMENT_SPECS)[0].text.split(" ")[0])

        return apartment


class Pararius(Target):

    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, 'pararius')
        if 'requestor' in kwargs:
            self.requestor = kwargs['requestor']
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page(self.config)
        extractor = SearchExtractor(capture)
        return extractor.get_advertisements()