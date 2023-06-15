import math
import time

from targets.pandomo import Pandomo
from targets.target import Config


def capture_result_page():
    capture_name = "pandomo_search_page_{}.html".format(math.floor(time.time()))
    with open(capture_name, "w") as capture:
        capture.write(pandomo.request_advertisement_page("stalstraat-52-312449").raw)

def capture_search_page():
    capture_name = "pandomo_search_page_{}.html".format(math.floor(time.time()))
    with open(capture_name, "w") as capture:
        capture.write(pandomo.request_search_page().raw)


config = Config(500, 1000, 30)
pandomo = Pandomo(config)
