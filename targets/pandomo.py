import requests
from lxml import html

from model.model import Advertisement, Apartment
from targets.target import Target


class Capture:

    raw: str
    content: html.HtmlElement

    def __init__(self, content: str) -> None:
        super().__init__()
        self.raw = content
        self.content = html.fromstring(content)


class Pandomo(Target):

    def request(self):
        return requests.get('url')

    def request_search_page(self) -> Capture:
        response = requests.get("https://www.pandomo.nl/huurwoningen/")
        return Capture(response.content.decode("utf-8"))

    def request_advertisement_page(self, advertisement_id: str):
        response = requests.get("https://www.pandomo.nl/huurwoningen/h/{}/".format(advertisement_id))
        return Capture(response.content.decode("utf-8"))

    def get_advertisements(self) -> list[Advertisement]:
        return []



class SearchExtractor:
    BASE_URL = "https://www.pandomo.nl"

    ADVERTISEMENT_BASE = "//li[@class='results__item']"
    ADVERTISEMENT_TITLE_URL = "./div/h3/a"
    ADVERTISEMENT_DESCRIPTION = "./div/p"
    ADVERTISEMENT_PRICE = "./div/p/strong"
    ADVERTISEMENT_SPECS = "./div/div[@class='results__item__info specs']/span[1]"

    capture: Capture

    def __init__(self, capture: Capture) -> None:
        super().__init__()
        self.capture = capture

    def get_advertisements(self) -> list[Advertisement]:
        nodes = self.capture.content.xpath(self.ADVERTISEMENT_BASE)
        results = []

        for node in nodes:
            results.append(self._advertisement_from_node(node))

        return results

    def _advertisement_from_node(self, node: html.HtmlElement) -> Advertisement:
        elements: list[html.HtmlElement] = node.xpath(SearchExtractor.ADVERTISEMENT_TITLE_URL)
        if len(elements) == 0:
            return Advertisement()
        else:
            title = node.xpath(self.ADVERTISEMENT_TITLE_URL)[0]
            advertisement = Advertisement()
            advertisement.url = self.BASE_URL + title.attrib['href']
            advertisement.price = float(str.strip(node.xpath(self.ADVERTISEMENT_PRICE)[0].text.split(" ")[0][1::]).replace(".", "").replace(',', '.'))
            advertisement.apartment = self._apartment_from_node(node)
            return advertisement

    def _apartment_from_node(self, node: html.HtmlElement) -> Apartment:
        apartment = Apartment()
        description: str = node.xpath(self.ADVERTISEMENT_DESCRIPTION)[0].text
        split: list[str] = description.replace("\n", "").split(" ")

        title = node.xpath(self.ADVERTISEMENT_TITLE_URL)[0]
        apartment.address = title.attrib['title']
        apartment.postal_code = str.join("", split[0:2])
        apartment.city = str.strip(str.join(" ", split[2::]).capitalize())
        apartment.size = int(node.xpath(self.ADVERTISEMENT_SPECS)[0].text.split(" ")[0])

        return apartment


    def get_nr_advertisements(self):
        return len(self.capture.content.xpath("//li[@class='results__item']"))
