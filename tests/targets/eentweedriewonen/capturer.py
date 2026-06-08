import math
import time

from targets.eentweedriewonen import HttpRequestor
from targets.target import TargetConfig

config = TargetConfig(500, 1250, 25)
requestor = HttpRequestor()

capture_name = "eentweedriewonen_search_page_{}.html".format(math.floor(time.time()))
with open(capture_name, "w") as capture:
    capture.write(requestor.request_search_page(config).raw)
