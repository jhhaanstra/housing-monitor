import re
from abc import ABC, abstractmethod
from typing import Literal

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
        session = requests.session()

        surface_url = self.build_search_url(config, "surface")
        session.get(surface_url, timeout=15)

        price_url = self.build_search_url(config, "price")
        response = session.get(price_url, timeout=15)

        return Capture(response.json()["html"])

    @staticmethod
    def build_search_url(config, spec: Literal["price", "surface"]):
        base_url = "https://www.123wonen.nl/assets/json/immozo/objects/list?jsonparams=1739-8169-1&urlparams=/huurwoningen/in/groningen"
        if spec == "price":
            url = base_url + f"?addspec=price/-/{config.min_price}-{config.max_price}"
        else:
            url = base_url + f"?addspec=size_m2/-/{config.min_surface}"
        return url



class SearchExtractor:
    _ADVERTISEMENT_BASE = "//div[@class='pandlist-container ']"
    _ADVERTISEMENT_URL = "./div/div/a"
    _ADVERTISEMENT_PRICE = "./div[@class='pand-price']/text()"
    _ADVERTISEMENT_SIZE = ".//div[@class='pand-specs']/ul/li[5]/span[2]/text()"
    _ADVERTISEMENT_ADDRESS = ".//span[@class='pand-address']/text()"
    _ADVERTISEMENT_CITY = ".//div[@class='pand-title']/text()"
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
        advertisement.price = self._price_from_node(node)
        advertisement.state = AdvertisementState.AVAILABLE
        advertisement.apartment = self._apartment_from_node(node)
        return advertisement

    def _extract_url(self, node: html.HtmlElement) -> str:
        url: str = node.xpath(self._ADVERTISEMENT_URL)[0].attrib["href"]
        return url

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()

        try:
            apartment.address = (
                node.xpath(self._ADVERTISEMENT_ADDRESS)[0].strip()
            )
        except IndexError:
            apartment.address = ""
        apartment.city = node.xpath(self._ADVERTISEMENT_CITY)[0].strip().split(',')[0]
        size_text = node.xpath(self._ADVERTISEMENT_SIZE)[0].strip()
        apartment.size = round(float(size_text.split(" ")[0].replace(",", ".")))

        return apartment

    def _price_from_node(self, node: html.HtmlElement) -> str:
        node_text = (
            str(node.xpath(self._ADVERTISEMENT_PRICE)[0])
            .strip()
            .split(",")[0]
            .replace(".", "")
        )
        # Extract the first number-like pattern
        match = re.search(r"([\d.,]+)", node_text)
        if match:  # "750,00"
            return match.group(1)
        else:
            raise ValueError(f"invalid price found {node_text}")


class EenTweeDrieWonen(Target):
    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, "123wonen")
        if "requestor" in kwargs:
            self.requestor = kwargs["requestor"]
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page(self.config)
        extractor = SearchExtractor(capture)
        return extractor.get_advertisements()
