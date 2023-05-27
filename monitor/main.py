import requests
from lxml import html

r = requests.get('http://example.org/')
tree = html.fromstring(r.content)
print(tree.xpath('//h1')[0].text)
