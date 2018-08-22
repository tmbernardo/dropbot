from lxml import html
from fbpage import page
from flask import Flask, request
import os
import time
import requests
import dbhandler as db

seconds = 15

def notify_all(diff):
    for user in db.get_table("users", "fb_id"):
        page.send(user, "\n".join(diff))
    print("All users notified")

def get_current():
    while(True):
        print("Checking if new products are on ACRNM")
        page = requests.get('http://acrnm.com')
        tree = html.fromstring(page.content)

        # create a list of products:
        cur_products = set(tree.xpath('//div[@class="name"]/text()'))
        old_prods = set(db.get_table("products","prod_name"))
        print("old prods")
        print(old_prods)
        print("cur_products")
        print(cur_products)
        if cur_products != old_prods:
            diff = list(cur_products.difference(old_prods))
            notify_all(diff)
            db.insert_list("products", "prod_name", diff)
        time.sleep(seconds)

if  __name__ == "__main__":
    db.create_tables()
    get_current()
