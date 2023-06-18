from abc import abstractmethod, ABC

import requests
from lxml import html

from model.model import Advertisement, Apartment, AdvertisementState
from targets.target import Target, Config


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
        response = requests.get("https://www.pandomo.nl/huurwoningen/")
        return Capture(response.content.decode("utf-8"))


class SearchExtractor:
    BASE_URL = "https://www.pandomo.nl"

    _ADVERTISEMENT_BASE = "//li[@class='results__item']"
    _ADVERTISEMENT_TITLE_URL = "./div/h3/a"
    _ADVERTISEMENT_DESCRIPTION = "./div/p"
    _ADVERTISEMENT_PRICE = "./div/p/strong"
    _ADVERTISEMENT_LABEL = "./a/div/*[contains(@class, 'image__label')]"
    _ADVERTISEMENT_SPECS = "./div/div[@class='results__item__info specs']/span[1]"

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
            advertisement.price = node.xpath(self._ADVERTISEMENT_PRICE)[0].text.replace(" ", "")
            advertisement.state = self._state_from_node(node)

            advertisement.apartment = self._apartment_from_node(node)
            return advertisement

    def _state_from_node(self, node: html.HtmlElement) -> AdvertisementState:
        label: str = node.xpath(self._ADVERTISEMENT_LABEL)[0].text.lower()
        match label:
            case "onder optie":
                return AdvertisementState.UNDER_OPTION
            case "verhuurd":
                return AdvertisementState.UNAVAILABLE
            case _:
                return AdvertisementState.AVAILABLE

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()
        description: str = node.xpath(self._ADVERTISEMENT_DESCRIPTION)[0].text.replace("\n", "")
        split: list[str] = description.replace("\n", "").split(" ")

        title = node.xpath(self._ADVERTISEMENT_TITLE_URL)[0]
        apartment.address = title.attrib["title"]
        apartment.postal_code = str.join("", split[0:2])
        apartment.city = str.strip(str.join(" ", split[2::]).capitalize())
        apartment.size = int(node.xpath(self._ADVERTISEMENT_SPECS)[0].text.split(" ")[0])

        return apartment


class Pandomo(Target):

    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: Config, requestor: Requestor):
        super().__init__(config)
        self.requestor = requestor

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page()
        extractor = SearchExtractor(capture)
        return extractor.get_advertisements()
