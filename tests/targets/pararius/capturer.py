import math
import time

from targets.pararius import HttpRequestor
from targets.target import TargetConfig

config = TargetConfig(800, 1000, 30)
requestor = HttpRequestor()

capture_name = "pararius_search_page_{}.html".format(math.floor(time.time()))
with open(capture_name, "w") as capture:
    capture.write(requestor.request_search_page(config).raw)
