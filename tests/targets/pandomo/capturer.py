import math
import time

from targets.pandomo import HttpRequestor
from targets.target import TargetConfig

config = TargetConfig(500, 1000, 30)
requestor = HttpRequestor()

capture_name = "pandomo_search_page_{}.html".format(math.floor(time.time()))
with open(capture_name, "w") as capture:
    capture.write(requestor.request_search_page().raw)
