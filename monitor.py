from flask import Flask, request
from lxml import html
import requests
import time
import dbhandler as db
import os

seconds = 30
def get_current():
    while(True):
        page = requests.get('http://acrnm.com')
        tree = html.fromstring(page.content)

        # create a list of products:
        cur_products = tree.xpath('//div[@class="name"]/text()')
        db.insert_list("products", "prod_name", cur_products)
        time.sleep(seconds)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
