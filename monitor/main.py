import time

import requests
from lxml import html

r = requests.get('https://www.pandomo.nl/huurwoningen/')
tree = html.fromstring(r.content)
print(tree.xpath('//h1')[0].text)

# Opening a file
with open('capture_' + int(time.time()) + '.txt', 'w') as file:
    file.writelines(r.content)
    file.close()