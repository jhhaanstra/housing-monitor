import math
import time

from targets.vandermeulen import HttpRequestor
from targets.target import TargetConfig

config = TargetConfig(600, 1200, 40)
requestor = HttpRequestor()

capture_name = "vandermeulen_search_page_{}.html".format(math.floor(time.time()))
with open(capture_name, "w") as capture:
    capture.write(requestor.request_search_page(config).raw)
