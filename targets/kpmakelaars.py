import json
from abc import abstractmethod, ABC

import requests
from lxml import html

from model.model import Advertisement, Apartment, AdvertisementState
from targets.target import Target, TargetConfig


class Capture:
    raw: str
    content: dict

    def __init__(self, content: str) -> None:
        super().__init__()
        self.raw = content
        self.content = json.JSONDecoder().decode(content)


class Requestor(ABC):

    @abstractmethod
    def request_search_page(self, config: TargetConfig) -> Capture:
        pass


class HttpRequestor(Requestor):

    def request_search_page(self, config: TargetConfig) -> Capture:
        search = self.build_search_query(config)

        response = requests.post('https://cdn.eazlee.com/eazlee/api/query_functions.php', data={
            "action": "all_locations",
            "search": search,
            "lang": "woningaanbod",
            "api": "8d26f881f5008508afd604a108ea5d06",
            "path":	"/woningaanbod",
            "center_map": "false"
        })

        return Capture(response.content.decode("utf-8"))

    def build_search_query(self, config: TargetConfig):
        return "min_price={min_price}&max_price={max_price}&min_area={size}".format(
            min_price=config.min_price,
            max_price=config.max_price,
            size=config.min_surface
        )


class SearchExtractor:
    def __init__(self, capture: Capture) -> None:
        super().__init__()
        self.capture = capture

    def get_advertisements(self) -> list[Advertisement]:
        return [self._advertisement_from_node(value) for key, value in self.capture.content.items() if key.isdigit()]

    def _advertisement_from_node(self, advertisement) -> Advertisement:
        _advertisement = Advertisement()
        _advertisement.url = "https://www.kpmakelaars.nl/woning/{city}-{street}-{id}".format(
            city=advertisement['city'],
            street=advertisement['street'],
            id=advertisement['house_id']
        )
        _advertisement.state = self._extract_state(advertisement['front_status'])
        _advertisement.price = '€' + advertisement['set_price']
        _advertisement.apartment = self._apartment_from_node(advertisement)
        return _advertisement

    def _extract_state(self, state: str):
        return AdvertisementState.AVAILABLE if not state else AdvertisementState.UNAVAILABLE


    def _apartment_from_node(self, advertisement) -> Apartment:
        apartment = Apartment()
        apartment.address = advertisement['street'] + " " + advertisement['number'] + '-' + advertisement['addition']
        apartment.postal_code = advertisement['zipcode']
        apartment.city = advertisement['city']
        apartment.size = int(advertisement['surface'])
        return apartment


class KpMakelaars(Target):

    requestor: Requestor
    extractor: SearchExtractor

    def __init__(self, config: TargetConfig, **kwargs):
        super().__init__(config, 'kpmakelaars')
        if 'requestor' in kwargs:
            self.requestor = kwargs['requestor']
        else:
            self.requestor = HttpRequestor()

    def get_advertisements(self) -> list[Advertisement]:
        capture: Capture = self.requestor.request_search_page(self.config)
        extractor = SearchExtractor(capture)
        return extractor.get_advertisements()