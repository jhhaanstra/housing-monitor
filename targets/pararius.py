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
        # url = self.build_search_url(config)
        url = "https://www.pararius.nl/huurwoningen/groningen/800-1300/30m2"
        headers = {
            "Host": "www.pararius.nl",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Pragma": "no-cache",
        }

        response = requests.get(url, headers=headers, timeout=15)
        return Capture(response.content.decode("utf-8"))

    @staticmethod
    def build_search_url(config: TargetConfig) -> str:
        return "https://www.pararius.nl/huurwoningen/groningen/{min_price}-{max_price}/{min_surface}m2".format(
            min_price=config.min_price,
            max_price=config.max_price,
            min_surface=config.min_surface,
        )


class SearchExtractor:
    BASE_URL = "https://www.pararius.com"
    _ADVERTISEMENT_BASE = "//ul[@class='search-list']/li/section"
    _ADVERTISEMENT_TITLE_URL = ".//h3/a"
    _ADVERTISEMENT_DESCRIPTION = "./div/div[contains(@class, 'sub-title')]"
    _ADVERTISEMENT_PRICE = "./div/div[contains(@class, 'price')]/span"
    _ADVERTISEMENT_LABEL = "./div[contains(@class, 'label')]/span"
    _ADVERTISEMENT_SPECS = (
        "./div/div[contains(@class, 'features')]/ul/li[contains(@class, 'surface')]"
    )

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
            advertisement.price = self._price_from_node(node)
            advertisement.state = AdvertisementState.AVAILABLE

            advertisement.apartment = self._apartment_from_node(node)
            return advertisement

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()
        description: str = node.xpath(self._ADVERTISEMENT_DESCRIPTION)[0].text.strip()
        split: list[str] = description.split(" ")

        title = node.xpath(self._ADVERTISEMENT_TITLE_URL)[0]
        apartment.address = title.text.strip()
        apartment.postal_code = str.join("", split[0:2])

        apartment.city = str.strip(str.join(" ", split[2::]).capitalize())
        apartment.size = int(
            node.xpath(self._ADVERTISEMENT_SPECS)[0].text.strip().split(" ")[0]
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


class Pararius(Target):
    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, "pararius")
        if "requestor" in kwargs:
            self.requestor = kwargs["requestor"]
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page(self.config)
        extractor = SearchExtractor(capture)
        return extractor.get_advertisements()
