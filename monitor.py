from flask import Flask, request
from lxml import html
from fbpage import page
import requests
import time
import dbhandler as db
import os

seconds = 60

def notify_all(diff):
    for user in db.get_table("fb_id", "users"):
        page.send(user, "\n".join(diff))
    print("All users notified")

def get_current():
    while(True):
        page = requests.get('http://acrnm.com')
        tree = html.fromstring(page.content)

        # create a list of products:
        cur_products = set(tree.xpath('//div[@class="name"]/text()'))
        old_prods = set(db.get_table("prod_name","products"))
        print(cur_products, old_prods)
        if cur_products & old_prods:
            diff = list(cur_products.difference(old_prods))
            notify_all(diff)
            db.insert_list("products", "prod_name", diff)
        time.sleep(seconds)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
