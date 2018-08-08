from lxml import html
import requests
import time

seconds = 1
previous_products = []

while(True):
    page = requests.get('http://acrnm.com')
    tree = html.fromstring(page.content)

    # This will create a list of products:
    cur_products = tree.xpath('//div[@class="name"]/text()')

    if(previous_products != cur_products):
        previous_products = cur_products
        # send notification to messenger

    # time.sleep(seconds)
    print(previous_products)
